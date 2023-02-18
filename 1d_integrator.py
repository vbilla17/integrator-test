import csv
import matplotlib.pyplot as plt
import math

def integrateAccel(az, accel_timestamps):
    last_accel = az[0]
    last_timestamp = accel_timestamps[0]
    current_vel = 0
    current_alt = 2060

    velocities = [0]  # initial velocity is 0
    altitudes = [current_alt]

    for i in range(1, len(accel_timestamps)):
        current_accel = az[i]
        current_timestamp = accel_timestamps[i]
        delta_t = (current_timestamp - last_timestamp)  # convert milliseconds to seconds
        # current_vel += delta_t * (last_accel + current_accel) / 2 - (gravVal(current_alt) * delta_t**2) / 2
        current_vel += delta_t * ((last_accel + current_accel) - (2 * gravVal(current_alt))) / 2
        # print(gravVal(current_alt))
        last_accel = current_accel
        last_timestamp = current_timestamp
        velocities.append(current_vel)
        if i > 2:
            current_alt += delta_t * (velocities[-2] + velocities[-1]) / 2
        else:
            current_alt = 2060  # reset altitude to initial value for first 3 iterations
        altitudes.append(current_alt)

    return velocities, altitudes

def latGravSurface(lat):
        # Cache sine squared of latitude bc we use it twice
        latSinSquare = math.pow(math.sin(lat*math.pi), 2)
        ge = 9.7803267715   # Equatorial gravity
        return ge*( (1 + 0.001931851353*latSinSquare)/ math.sqrt(1 - 0.0066943800229*latSinSquare))

def gravVal(h):
    lat = 35.3467755
    mToFt = 3.28084
    a = 6378.137    # Equatorial radius [km]
    b = 6356.7523   # Polar radius [km]
    gSurf = latGravSurface(lat)
    sinLat = math.sin(lat*math.pi)
    cosLat = math.cos(lat*math.pi)
    rActual = math.sqrt( (math.pow(a*a*cosLat, 2) + math.pow(b*b*sinLat, 2))/ ( math.pow(a*cosLat, 2) + math.pow(b*sinLat,2)) ) # Earth radius at given latitude
    # Return gravity in ft/s^2
    return gSurf*mToFt*math.pow( (rActual*1000*mToFt)/(h + rActual*1000*mToFt), 2 )

def correctTimestamps(accel_timestamps):
    first_timestamp = accel_timestamps[0]

    for i in range(0, len(accel_timestamps)):
        accel_timestamps[i] -= first_timestamp
        accel_timestamps[i] *= 0.000001

def trimAccel(az, accel_timestamps, start_time, end_time):
    for i in range(0, len(accel_timestamps)):
        if accel_timestamps[i] <= start_time:
            start_idx = i
        else: break

    for i in range(0, len(accel_timestamps)):
        if accel_timestamps[i] <= end_time:
            end_idx = i
        else: break

    return az[start_idx:end_idx], accel_timestamps[start_idx:end_idx]

def correctAccel(az):
    for i in range(0, len(az)):
        az[i] *= -0.03217405 # for adis z acce;
        # az[i] *= 0.06284 # for kx z acce;

def correctGps(gps_alt):
    for i in range(0, len(gps_alt)):
        gps_alt[i] *= 0.00328084

def plotAcc(acc_x, acc_y, acc_z, accel_timestamps, title):
    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, acc_x, label='acc_x')
    plt.plot(accel_timestamps, acc_y, label='acc_y')
    plt.plot(accel_timestamps, acc_z, label='acc_z')
    plt.legend()
    plt.title(title)
    plt.show()

def main():
    accel_input_path = 'input/Jawbone/ADIS-trimmed.csv'

    accel_timestamps = []
    accel_packets = []
    ax = []
    ay = []
    az = []

    with open(accel_input_path, 'r') as accel_file:
        reader = csv.reader(accel_file)

        headers = next(reader)
        power_ctr_idx = headers.index('pwr_ctr')

        row = next(reader)
        first_timestamp = float(row[power_ctr_idx])

    print("First Timestamp: ", first_timestamp)

    # reads in accel data and timestamps
    with open(accel_input_path, 'r') as accel_file:
        accel_reader = csv.reader(accel_file)

        headers = next(accel_reader)
        flight_ctr_idx = headers.index('flight_ctr')
        ax_idx = headers.index('ax')
        ay_idx = headers.index('ay')
        az_idx = headers.index('az')
        checksum_idx = headers.index('Checksum Status')
        packet_idx = headers.index('Packet #')
        power_ctr_idx = headers.index('pwr_ctr')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(float(row[flight_ctr_idx]))
                ax.append(float(row[ax_idx]))
                ay.append(float(row[ay_idx]))
                az.append(float(row[az_idx]))
                accel_packets.append(float(row[packet_idx]))

        if not (len(accel_timestamps) == len(ax) == len(ay) == len(az)):
            print("Acceleration and timestamp lists are different lengths!!")
            return 1
        else:
            print("Accel data read!")

    gps_input_path = 'input/Jawbone/GPS-trimmed.csv'

    gps_timestamps = []
    gps_alt = []

    with open(gps_input_path, 'r') as gps_file:
        gps_reader = csv.reader(gps_file)

        headers = next(gps_reader)
        flight_ctr_idx = headers.index('flight_ctr')
        checksum_idx = headers.index('Checksum Status')
        alt_idx = headers.index('height')

        for row in gps_reader:
            if row[checksum_idx] == 'OK':
                gps_timestamps.append(float(row[flight_ctr_idx]))
                gps_alt.append(float(row[alt_idx]))

    print("GPS data read!")

    print("Accel length: ", len(accel_timestamps))

    correctTimestamps(accel_timestamps)
    correctTimestamps(gps_timestamps)

    correctAccel(az)
    correctGps(gps_alt)

    az, accel_timestamps = trimAccel(az, accel_timestamps, 0, 60)

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, az)
    plt.title("Accel")
    plt.show()

    velocities, altitudes = integrateAccel(az, accel_timestamps)

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, velocities)
    plt.title("Velocity")
    plt.show()

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, altitudes, label = "integrated")
    plt.plot(gps_timestamps, gps_alt, label = "GPS")
    plt.title("Altitude")
    plt.legend()
    plt.show()

    print("Max Velocity: ", max(velocities), " at ", accel_timestamps[velocities.index(max(velocities))], "s")
    print("Max Altitude: ", max(altitudes), " at ", accel_timestamps[altitudes.index(max(altitudes))], "s")

if __name__ == "__main__":
    main()