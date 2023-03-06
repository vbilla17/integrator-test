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

    # print("start idx: ", start_idx)
    # print("end idx: ", end_idx)

    data = data[start_idx:end_idx]
    timestamps = timestamps[start_idx:end_idx]
    return data, timestamps

def trimAccel(accel, timestamps, start_time, end_time, offset):
    us_to_s = 0.000001

    correctTimestamps(timestamps, us_to_s, offset)

    start_idx = 0
    end_idx = len(timestamps) - 1
    for i in range(0, len(timestamps)):
        if timestamps[i] <= start_time:
            start_idx = i
        else:
            break

    for i in range(0, len(timestamps)):
        if timestamps[i] > end_time:
            end_idx = i
            break

    # print("Acc start idx: ", start_idx)
    # print("Acc end idx: ", end_idx)

    accel = [a[start_idx:end_idx] for a in accel]
    timestamps = timestamps[start_idx:end_idx]
    return accel, timestamps

def correctAccel(accel, flight, sensor):
    if flight == "JAWBONE":
        if sensor == "ADIS":
            conversion_factors = [0.03217405,0.03217405,-0.03217405]
            # conversion_factors = [0.03217405,0.03217405,-0.03303405] # corrected to match gps
        elif sensor == "ACCEL":
            conversion_factors = [0.06284,0.06284,0.06284] # theoretical
            # conversion_factors = [0.06284,0.06284,0.060194] # corrected to match gps
    elif flight == "CTRL-V":
        if sensor == "ADIS":
            conversion_factors = [0.032174,0.032174,-0.032174]
        elif sensor == "ACCEL":
            conversion_factors = [0.06039,0.06663,0.06284] # theoretical
            # conversion_factor = [0.06039,0.06663,0.06602]
    elif flight == "POISE":
        if sensor == "ADIS":
            conversion_factors = [0.06284,0.06284,0.06284]
        elif sensor == "ACCEL":
            conversion_factors = [1.6087,1.6087,1.6087]
    elif flight == "T4":
        if sensor == "ACCEL":
            conversion_factors = [1.6087,1.6087,1.5765]
            # conversion_factors = [1.6119,1.6415,1.5588]
    else:
        print("How did we get here???")
        return

    for i in range(len(accel)):
        for j in range(len(accel[i])):
            accel[i][j] *= conversion_factors[i]

def correctGps(gps_alt, flight):
    if flight == "JAWBONE" or "CTRL-V":
        conversion_factor = 0.00328084 # ZED-F9P conversion Jawbone, Ctrl-V
    elif flight == "POISE" or "T4":
        conversion_factor = 3280.84 # FGPMMOPA6H conversion Poise, T4
    else:
        print("How did we get here???")
        return

    for i in range(0, len(gps_alt)):
        gps_alt[i] *= conversion_factor

def correctBaro(baro_alt):
    for i in range(0, len(baro_alt)):
        baro_alt[i] *= 3.28084 # Baro conversion all flights
