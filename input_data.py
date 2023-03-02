import csv

def isValidInput(flight, sensor):
    if flight == "JAWBONE" and sensor == "ADIS" or "ACCEL":
        return True
    elif flight == "CTRL-V" and sensor == "ADIS" or "ACCEL":
        return True
    elif flight == "POISE" and sensor == "ADIS" or "ACCEL":
        return True
    elif flight == "T4" and sensor == "ACCEL":
        return True
    else:
        print("Error: Invalid flight and sensor combination!!")
        return False

def inputAccel(flight, sensor):
    if flight == "JAWBONE":
        if sensor == "ADIS":
            accel_input_path = 'input/jawbone/ADIS-trimmed.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/jawbone/ACCEL-trimmed.csv'
    elif flight == "CTRL-V":
        if sensor == "ADIS":
            accel_input_path = 'input/ctrl-v/ADIS-trimmed.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/ctrl-v/ACCEL-trimmed.csv'
    elif flight == "POISE":
        if sensor == "ADIS":
            accel_input_path = 'input/poise/ADIS.csv'
        elif sensor == "ACCEL":
            accel_input_path = 'input/poise/ACCEL.csv'
    elif flight == "T4":
        if sensor == "ACCEL":
            accel_input_path = 'input/t4/ACCEL.csv'
    else:
        print("How did we get here???")
        return

    print("Reading accel data from ", accel_input_path)

    accel_timestamps = []
    az = []

    # reads in accel data and timestamps
    with open(accel_input_path, 'r') as accel_file:
        accel_reader = csv.reader(accel_file)

        headers = next(accel_reader)
        az_idx = headers.index('az')
        checksum_idx = headers.index('Checksum Status')
        power_ctr_idx = headers.index('pwr_ctr')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(float(row[power_ctr_idx]))
                az.append(float(row[az_idx]))

        if not (len(accel_timestamps) == len(az)):
            print("Acceleration and timestamp lists are different lengths!!")
            return 1
        else:
            print("Accel data read!")

        return az, accel_timestamps

def inputGps(flight):
    print(flight)
    if flight == "JAWBONE":
        gps_input_path = 'input/jawbone/GPS-trimmed.csv'
    elif flight == "CTRL-V":
        gps_input_path = 'input/ctrl-v/GPS-trimmed.csv'
    elif flight == "POISE":
        gps_input_path = 'input/poise/GPS.csv'
    elif flight == "T4":
        gps_input_path = 'input/t4/GPS.csv'

    print("Reading GPS data from ", gps_input_path)

    gps_timestamps = []
    gps_alt = []

    with open(gps_input_path, 'r') as gps_file:
        gps_reader = csv.reader(gps_file)

        headers = next(gps_reader)
        checksum_idx = headers.index('Checksum Status')
        if flight == "JAWBONE" or "CTRL-V":
            alt_idx = headers.index('height') # Jawbone and Ctrl-V
        elif flight == "POISE" or "T4":
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
    if flight == "JAWBONE":
        baro_input_path = 'input/jawbone/BARO-trimmed.csv'
    elif flight == "CTRL-V":
        baro_input_path = 'input/ctrl-v/BARO.csv'
    elif flight == "POISE":
        baro_input_path = 'input/poise/BARO.csv'
    elif flight == "T4":
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
    if flight == "JAWBONE":
        return [0, 60, -36284.4]
    elif flight == "CTRL-V":
        return [0, 50, -66991.6]
    elif flight == "POISE":
        return [-10,1000, 0]
    elif flight == "T4":
        return [-10,150, -84169.48]