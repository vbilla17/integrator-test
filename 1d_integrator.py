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
        delta_t = (current_timestamp - last_timestamp)
        current_vel += delta_t * ((last_accel + current_accel) - (2 * gravVal(current_alt))) / 2
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

def correctTimestamps(timestamps, conversion, offset):
    # print(timestamps[0])
    for i in range(0, len(timestamps)):
        timestamps[i] *= conversion
        timestamps[i] += offset
    # print(timestamps[0])

def trimData(data, timestamps, start_time, end_time, offset):
    us_to_s = 0.000001

    correctTimestamps(timestamps, us_to_s, offset)

    start_idx = 0
    end_idx = len(data) - 1
    for i in range(0, len(timestamps)):
        if timestamps[i] <= start_time:
            start_idx = i
        else:
            break

    for i in range(0, len(timestamps)):
        if timestamps[i] > end_time:
            end_idx = i
            break

    # print("Start idx: ", start_idx)
    # print("End idx: ", end_idx)

    data = data[start_idx:end_idx]
    timestamps = timestamps[start_idx:end_idx]
    # print("First timestamp: ", timestamps[0], "s")
    # print("Last timestamp: ", timestamps[-1], "s")
    return data, timestamps


def correctAccel(az):
    for i in range(0, len(az)):
        az[i] *= -0.03217405 # for adis z accel Jawbone;
        # az[i] *= -0.032174 # for adis z accel Ctrl-V, Poise;
        # az[i] *= 0.06284 # for kx z accel Jawbone;
        # az[i] *= 0.059 # for kx test;
        # az[i] *= 0.06602 # for kx z accel Ctrl-V;
        # az[i] *= 1.6087 # for ADXL z accel Poise
        # az[i] *= 1.5588 # for ADXL z accel T4
        # az[i] *= 1.61 # for ADXL z accel test

def correctGps(gps_alt):
    for i in range(0, len(gps_alt)):
        gps_alt[i] *= 0.00328084 # ZED-F9P conversion Jawbone, Ctrl-V
        # gps_alt[i] *= 3280.84 # FGPMMOPA6H conversion Poise, T4

def correctBaro(baro_alt):
    for i in range(0, len(baro_alt)):
        baro_alt[i] *= 3.28084 # Baro conversion all flights

def main():
    accel_input_path = 'input/Jawbone/ADIS-trimmed.csv'
    # accel_input_path = 'input/Jawbone/ACCEL-trimmed.csv'
    # accel_input_path = 'input/ctrl-v/ADIS-trimmed.csv'
    # accel_input_path = 'input/ctrl-v/ACCEL-trimmed.csv'
    # accel_input_path = 'input/poise/ADIS.csv'
    # accel_input_path = 'input/poise/ACCEL.csv'
    # accel_input_path = 'input/t4/ACCEL.csv'

    print("Reading accel data from ", accel_input_path)

    accel_timestamps = []
    accel_packets = []
    az = []

    # reads in accel data and timestamps
    with open(accel_input_path, 'r') as accel_file:
        accel_reader = csv.reader(accel_file)

        headers = next(accel_reader)
        az_idx = headers.index('az')
        checksum_idx = headers.index('Checksum Status')
        packet_idx = headers.index('Packet #')
        power_ctr_idx = headers.index('pwr_ctr')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(float(row[power_ctr_idx]))
                az.append(float(row[az_idx]))
                accel_packets.append(float(row[packet_idx]))

        if not (len(accel_timestamps) == len(az)):
            print("Acceleration and timestamp lists are different lengths!!")
            return 1
        else:
            print("Accel data read!")

    gps_input_path = 'input/Jawbone/GPS-trimmed.csv'
    # gps_input_path = 'input/ctrl-v/GPS-trimmed.csv'
    # gps_input_path = 'input/poise/GPS.csv'
    # gps_input_path = 'input/t4/GPS.csv'

    print("Reading GPS data from ", gps_input_path)

    gps_timestamps = []
    gps_alt = []

    with open(gps_input_path, 'r') as gps_file:
        gps_reader = csv.reader(gps_file)

        headers = next(gps_reader)
        checksum_idx = headers.index('Checksum Status')
        alt_idx = headers.index('height') # Jawbone and Ctrl-V
        # alt_idx = headers.index('altitude') # Poise and T4
        power_ctr_idx = headers.index('pwr_ctr')

        for row in gps_reader:
            if row[checksum_idx] == 'OK':
                gps_timestamps.append(float(row[power_ctr_idx]))
                gps_alt.append(float(row[alt_idx]))

        if not (len(gps_timestamps) == len(gps_alt)):
            print("GPS and timestamp lists are different lengths!!")
            return 1
        else:
            print("GPS data read!")

    baro_input_path = 'input/Jawbone/BARO-trimmed.csv'
    # baro_input_path = 'input/ctrl-v/BARO.csv'
    # baro_input_path = 'input/poise/BARO.csv'
    # baro_input_path = 'input/t4/BARO.csv'

    print("Reading baro data from ", baro_input_path)

    baro_timestamps = []
    baro_alt = []

    with open(baro_input_path, 'r') as baro_file:
        baro_reader = csv.reader(baro_file)

        headers = next(baro_reader)
        checksum_idx = headers.index('Checksum Status')
        alt_idx = headers.index('altitude')
        power_ctr_idx = headers.index('pwr_ctr')

        for row in baro_reader:
            if row[checksum_idx] == 'OK':
                baro_timestamps.append(float(row[power_ctr_idx]))
                baro_alt.append(float(row[alt_idx]))

        if not (len(baro_timestamps) == len(baro_alt)):
            print("BARO and timestamp lists are different lengths!!")
            return 1
        else:
            print("BARO data read!")

    # Timescale parameters, format is [start time, end time, offset(us)]
    Timescale = [0, 60, -36284.4] # for Jawbone
    # Timescale = [0, 60, -66991.6] # for Ctrl-V
    # Timescale = [-10,1000, 0] # for Poise
    # Timescale = [-10,150, -84169.48] # for T4

    az, accel_timestamps = trimData(az, accel_timestamps, Timescale[0], Timescale[1], Timescale[2])
    gps_alt, gps_timestamps = trimData(gps_alt, gps_timestamps, Timescale[0], Timescale[1], Timescale[2])
    baro_alt, baro_timestamps = trimData(baro_alt, baro_timestamps, Timescale[0], Timescale[1], Timescale[2])

    correctAccel(az)
    correctGps(gps_alt)
    correctBaro(baro_alt)

    velocities, altitudes = integrateAccel(az, accel_timestamps)

    print("Max Integrated Velocity: ", max(velocities), " at ", accel_timestamps[velocities.index(max(velocities))], "s")
    print("Max Integrated Altitude: ", max(altitudes), " at ", accel_timestamps[altitudes.index(max(altitudes))], "s")

    print("Max GPS Altitude: ", max(gps_alt), " at ", gps_timestamps[gps_alt.index(max(gps_alt))], "s")
    print("Max Baro Altitude: ", max(baro_alt), " at ", baro_timestamps[baro_alt.index(max(baro_alt))], "s")

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, az)
    plt.title("Accel")

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, velocities)
    plt.title("Velocity")

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, altitudes, label = "integrated")
    plt.plot(gps_timestamps, gps_alt, label = "GPS")
    plt.plot(baro_timestamps, baro_alt, label = "BARO")
    plt.title("Altitude")
    plt.legend()

    plt.show()

if __name__ == "__main__":
    main()