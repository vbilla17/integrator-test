import csv
import matplotlib.pyplot as plt
import math


class Vector3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
class Quaternion4D:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

def rotateVector(q, v):
    ans = Vector3D(0, 0, 0)
    q1 = multiplyQuaternionsByVec(q, v)
    q2 = conjugateQuaternions(q)
    q3 = multiplyQuaternions(q1, q2)
    ans.x = q3.x
    ans.y = q3.y
    ans.z = q3.z
    return ans
def multiplyQuaternionsByVec(q, v):
    ans = Quaternion4D(0, 0, 0, 0)
    ans.w = -q.x * v.x - q.y * v.y - q.z * v.z
    ans.x = q.w * v.x + q.y * v.z - q.z * v.y
    ans.y = q.w * v.y - q.x * v.z + q.z * v.x
    ans.z = q.w * v.z + q.x * v.y - q.y * v.x
    return ans
def conjugateQuaternions(q):
    ans = Quaternion4D(0, 0, 0, 0)
    ans.w = q.w
    ans.x = -q.x
    ans.y = -q.y
    ans.z = -q.z
    return ans
def multiplyQuaternions(q1, q2):
    ans = Quaternion4D(0, 0, 0, 0)
    ans.w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
    ans.x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
    ans.y = q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x
    ans.z = q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w
    return ans
def integrateAccelWithQuaternions(start_alt, ax, ay, az, accel_timestamps, quantVec):
    last_accel_x = ax[0]
    last_accel_y = ay[0]
    last_accel_z = az[0]
    last_quant = quantVec[0]
    vec = Vector3D(last_accel_x, last_accel_y, last_accel_z)

    last_timestamp = accel_timestamps[0]
    current_vel = 0
    current_alt = start_alt

    velocities = [0]  # initial velocity is 0
    altitudes = [current_alt]

    for i in range(1, len(accel_timestamps)):
        current_accel_x = ax[i]
        current_accel_y = ay[i]
        current_accel_z = az[i]
        current_timestamp = accel_timestamps[i]
        delta_t = (current_timestamp - last_timestamp)
        newAccelWorld = rotateVector(last_quant, vec)

        current_vel += delta_t * ((last_accel_z + newAccelWorld.z) - (2 * gravVal(current_alt))) / 2

        last_accel_x = current_accel_x
        last_accel_y = current_accel_y
        last_accel_z = current_accel_z

        vec.x = last_accel_x
        vec.y = last_accel_y
        vec.z = last_accel_z

        last_timestamp = current_timestamp
        velocities.append(current_vel)
        if i > 2:
            current_alt += delta_t * (velocities[-2] + velocities[-1]) / 2
        else:
            current_alt = start_alt  # reset altitude to initial value for first 3 iterations
        altitudes.append(current_alt)

    return velocities, altitudes

def integrateAccel(start_alt, az, accel_timestamps):
    last_accel = az[0]
    last_timestamp = accel_timestamps[0]
    current_vel = 0
    current_alt = start_alt

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
            current_alt = start_alt  # reset altitude to initial value for first 3 iterations
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

def endBurnIndex(accel_timestamps, end_burn_time):
    end_idx = 0
    for i in range(0, len(accel_timestamps)):
        if accel_timestamps[i] < end_burn_time:
            end_idx = i
        else:
            break

    return end_idx

def correctAccel(az, flight, sensor):
    if flight == "Jawbone":
        if sensor == "ADIS":
            conversion_factor = -0.03217405
            # conversion_factor = -0.03303405 # corrected to match gps
        elif sensor == "ACCEL":
            conversion_factor = 0.06284
            # conversion_factor = 0.060194 # corrected to match gps
        elif sensor == "BNO":
            conversion_factor = 3.28084

    elif flight == "ctrl-v":
        if sensor == "ADIS":
            conversion_factor = -0.032174
        elif sensor == "ACCEL":
            conversion_factor = 0.06602

    elif flight == "poise":
        if sensor == "ADIS":
            conversion_factor = -0.032174
        elif sensor == "ACCEL":
            conversion_factor = 1.6087

    elif flight == "t4":
        if sensor == "ACCEL":
            conversion_factor = 1.5588

    else:
        print("How did we get here???")
        return

    for i in range(0, len(az)):
        az[i] *= conversion_factor

def correctGps(gps_alt, flight):
    if flight == "Jawbone" or "poise":
        conversion_factor = 0.00328084 # ZED-F9P conversion Jawbone, Ctrl-V
    elif flight == "poise" or "t4":
        conversion_factor = 3280.84 # FGPMMOPA6H conversion Poise, T4
    else:
        print("How did we get here???")
        return

    for i in range(0, len(gps_alt)):
        gps_alt[i] *= conversion_factor

def correctBaro(baro_alt):
    for i in range(0, len(baro_alt)):
        baro_alt[i] *= 3.28084 # Baro conversion all flights

def isValidInput(flight, sensor):
    if flight == "Jawbone" and sensor == "ADIS" or "ACCEL" or "BNO":
        return True
    elif flight == "ctrl-v" and sensor == "ADIS" or "ACCEL" or "BNO":
        return True
    elif flight == "poise" and sensor == "ADIS" or "ACCEL":
        return True
    elif flight == "t4" and sensor == "ACCEL":
        return True
    else:
        print("Error: Invalid flight and sensor combination!!")
        return False

def inputAccel3D(flight, sensor):
    if flight == "Jawbone":
        if sensor == "ADIS":
            accel_input_path = 'input/jawbone/ADIS-trimmed.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/jawbone/ACCEL-trimmed.csv'
        elif sensor == "BNO":
            accel_input_path = 'input/jawbone/BNO-trimmed.csv'
    elif flight == "ctrl-v":
        if sensor == "ADIS":
            accel_input_path = 'input/ctrl-v/ADIS-trimmed.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/ctrl-v/ACCEL-trimmed.csv'
        elif sensor == "BNO":
            accel_input_path = 'input/ctrl-v/BNO-trimmed.csv'
    elif flight == "poise":
        if sensor == "ADIS":
            accel_input_path = 'input/poise/ADIS.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/poise/ACCEL.csv'
    elif flight == "t4":
        if sensor == "ACCEL":
            accel_input_path = 'input/t4/ACCEL.csv'
    else:
        print("How did we get here???")
        return

    print("Reading accel data from ", accel_input_path)

    accel_timestamps = []
    accel_packets = []

    ax = []
    ay = []
    az = []
    q = []

    if sensor == "BNO":
        with open(accel_input_path, 'r') as accel_file:
            accel_reader = csv.reader(accel_file)

            headers = next(accel_reader)
            qw = headers.index('quantW')
            qx = headers.index('quantX')
            qy = headers.index('quantY')
            qz = headers.index('quantZ')
            checksum_idx = headers.index('Checksum Status')
            temp = Quaternion4D(qw, qx, qy, qz)
            for row in accel_reader:
                if row[checksum_idx] == 'OK':
                    q.append(Quaternion4D(row[qw], row[qw], row[qy], row[qz]))


    # reads in accel data and timestamps
    with open(accel_input_path, 'r') as accel_file:
        accel_reader = csv.reader(accel_file)

        headers = next(accel_reader)
        ax_idx = headers.index('ax')
        ay_idx = headers.index('ay')
        az_idx = headers.index('az')
        checksum_idx = headers.index('Checksum Status')
        packet_idx = headers.index('Packet #')
        power_ctr_idx = headers.index('pwr_ctr')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(float(row[power_ctr_idx]))
                ax.append(float(row[ax_idx]))
                ay.append(float(row[ay_idx]))
                az.append(float(row[az_idx]))
                accel_packets.append(float(row[packet_idx]))

        if not (len(accel_timestamps) == len(az)):
            print("Acceleration and timestamp lists are different lengths!!")
            return 1
        else:
            print("Accel data read!")

        return ax, ay, az, accel_packets, accel_timestamps, q
def inputAccel(flight, sensor):
    if flight == "Jawbone":
        if sensor == "ADIS":
            accel_input_path = 'input/jawbone/ADIS-trimmed.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/jawbone/ACCEL-trimmed.csv'
    elif flight == "ctrl-v":
        if sensor == "ADIS":
            accel_input_path = 'input/ctrl-v/ADIS-trimmed.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/ctrl-v/ACCEL-trimmed.csv'
    elif flight == "poise":
        if sensor == "ADIS":
            accel_input_path = 'input/poise/ADIS.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/poise/ACCEL.csv'
    elif flight == "t4":
        if sensor == "ACCEL":
            accel_input_path = 'input/t4/ACCEL.csv'
    else:
        print("How did we get here???")
        return

    print("Reading accel data from ", accel_input_path)

    accel_timestamps = []
    accel_packets = []

    ax = []
    ay = []
    az = []

    # reads in accel data and timestamps
    with open(accel_input_path, 'r') as accel_file:
        accel_reader = csv.reader(accel_file)

        headers = next(accel_reader)
        ax_idx = headers.index('ax')
        ay_idx = headers.index('ay')
        az_idx = headers.index('az')
        checksum_idx = headers.index('Checksum Status')
        packet_idx = headers.index('Packet #')
        power_ctr_idx = headers.index('pwr_ctr')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(float(row[power_ctr_idx]))
                ax.append(float(row[ax_idx]))
                ay.append(float(row[ay_idx]))
                az.append(float(row[az_idx]))
                accel_packets.append(float(row[packet_idx]))

        if not (len(accel_timestamps) == len(az)):
            print("Acceleration and timestamp lists are different lengths!!")
            return 1
        else:
            print("Accel data read!")

        return az, accel_packets, accel_timestamps

def inputGps(flight):
    if flight == "Jawbone":
        gps_input_path = 'input/jawbone/GPS-trimmed.csv'
    elif flight == "ctrl-v":
        gps_input_path = 'input/ctrl-v/GPS-trimmed.csv'
    elif flight == "poise":
        gps_input_path = 'input/poise/GPS.csv'
    elif flight == "t4":
        gps_input_path = 'input/t4/GPS.csv'

    print("Reading GPS data from ", gps_input_path)

    gps_timestamps = []
    gps_alt = []

    with open(gps_input_path, 'r') as gps_file:
        gps_reader = csv.reader(gps_file)

        headers = next(gps_reader)
        checksum_idx = headers.index('Checksum Status')
        if flight == "Jawbone" or "ctrl-v":
            alt_idx = headers.index('height') # Jawbone and Ctrl-V
        elif flight == "poise" or "t4":
            alt_idx = headers.index('altitude') # Poise and T4
        else:
            print("How did we get here??")
            return
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

        return gps_alt, gps_timestamps

def inputBaro(flight):
    if flight == "Jawbone":
        baro_input_path = 'input/jawbone/BARO-trimmed.csv'
    elif flight == "ctrl-v":
        baro_input_path = 'input/ctrl-v/BARO.csv'
    elif flight == "poise":
        baro_input_path = 'input/poise/BARO.csv'
    elif flight == "t4":
        baro_input_path = 'input/t4/BARO.csv'
    else:
        print("How did we get here???")
        return

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

    return baro_alt, baro_timestamps

def setTimescale(flight):
    # Timescale parameters, format is [start time, end time, offset(us)]
    if flight == "Jawbone":
        return [0, 60, -36284.4]
    elif flight == "ctrl-v":
        return [0, 50, -66991.6]
    elif flight == "poise":
        return [-10,1000, 0]
    elif flight == "t4":
        return [-10,150, -84169.48]

def printMaxes(az, velocities, altitudes, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps):
    max_accel = max(az[0:endBurnIndex(accel_timestamps, 15)])
    max_accel_g = max_accel * 0.031080950171567

    print("Max Accel: ", max_accel_g, "g at ", accel_timestamps[az.index(max_accel)], "s")
    print("Max Integrated Velocity: ", max(velocities), " at ", accel_timestamps[velocities.index(max(velocities))], "s")
    print("Max Integrated Altitude: ", max(altitudes), " at ", accel_timestamps[altitudes.index(max(altitudes))], "s")

    print("Max GPS Altitude: ", max(gps_alt), " at ", gps_timestamps[gps_alt.index(max(gps_alt))], "s")
    print("Max Baro Altitude: ", max(baro_alt), " at ", baro_timestamps[baro_alt.index(max(baro_alt))], "s")

def makePlots(az, velocities, altitudes, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps):
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

def main():

    flight = input("Enter the flight name to plot: ")
    sensor = input("Enter the sensor type to use (ADIS/ACCEL/BNO): ")

    if isValidInput(flight, sensor):

        q = Quaternion4D(0,0,0,0)
        ax, ay, az, accel_packets, accel_timestamps, q = inputAccel3D(flight, sensor)
        # az, accel_packets, accel_timestamps = inputAccel(flight, sensor)
        gps_alt, gps_timestamps = inputGps(flight)
        baro_alt, baro_timestamps = inputBaro(flight)

        timescale = setTimescale(flight)

        ax, accel_timestamps = trimData(ax, accel_timestamps, timescale[0], timescale[1], timescale[2])
        ay, accel_timestamps = trimData(ay, accel_timestamps, timescale[0], timescale[1], timescale[2])
        az, accel_timestamps = trimData(az, accel_timestamps, timescale[0], timescale[1], timescale[2])
        gps_alt, gps_timestamps = trimData(gps_alt, gps_timestamps, timescale[0], timescale[1], timescale[2])
        baro_alt, baro_timestamps = trimData(baro_alt, baro_timestamps, timescale[0], timescale[1], timescale[2])

        correctAccel(ax, flight, sensor)
        correctAccel(ay, flight, sensor)
        correctAccel(az, flight, sensor)
        correctGps(gps_alt, flight)
        correctBaro(baro_alt)

        velocities, altitudes = integrateAccelWithQuaternions(gps_alt[0], ax, ay, az, accel_timestamps, q)

        printMaxes(az, velocities, altitudes, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps)

        makePlots(az, velocities, altitudes, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps)
    else:
        print("ERROR: INVALID INPUT")
        return 1

if __name__ == "__main__":
    main()