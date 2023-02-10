import csv
import matplotlib.pyplot as plt
import math

def interpolate(qx, qy, qz, qw, ax, ay, az, bno_packets, accel_packets):
    first_packet_num = min(bno_packets[0], accel_packets[0])
    last_packet_num = max(bno_packets[-1], accel_packets[-1])

    qx_interpolated = []
    qy_interpolated = []
    qz_interpolated = []
    qw_interpolated = []
    ax_interpolated = []
    ay_interpolated = []
    az_interpolated = []

    for i in range()

def plotBno(qx, qy, qz, qw, bno_timestamps):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(qx, label='quat_x')
    ax.plot(qy, label='quat_y')
    ax.plot(qz, label='quat_z')
    ax.plot(qw, label='quat_w')
    # ax.plot(quat_sum_sq[0:2300], label='quat sum sq')

    ax.legend()

    # show the plot
    plt.show()
    print("Plotted BNO!")

def plotAcc(acc_x, acc_y, acc_z, accel_timestamps):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(acc_x[0:2300], label='acc_x')
    ax.plot(acc_y[0:2300], label='acc_y')
    ax.plot(acc_z[0:2300], label='acc_z')

def main():
    accel_input_path = 'input/ctrl-v/ACCEL-trimmed.csv'
    bno_input_path = 'input/ctrl-v/BNO-trimmed.csv'

    accel_timestamps = []
    bno_timestamps = []
    accel_packets = []
    bno_packets = []
    ax = []
    ay = []
    az = []
    quat_x = []
    quat_y = []
    quat_z = []
    quat_w = []
    quat_sum_sq = []

    # reads in accel data and timestamps
    with open(accel_input_path, 'r') as accel_file:
        accel_reader = csv.reader(accel_file)

        headers = next(accel_reader)
        flight_ctr_idx = headers.index('flight_ctr')
        ax_idx = headers.index('ax')
        ay_idx = headers.index('ay')
        az_idx = headers.index('az')
        checksum_idx = headers.index('Checksum Status')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(row[flight_ctr_idx])
                ax.append(row[ax_idx])
                ay.append(row[ay_idx])
                az.append(row[az_idx])

        if not (len(accel_timestamps) == len(ax) == len(ay) == len(az)):
            print("Acceleration and timestamp lists are different lengths!!")
            return 1
        else:
            print("Accel data read!")

    # reads in bno data and timestamps
    with open(bno_input_path, 'r') as bno_file:
        bno_reader = csv.reader(bno_file)

        headers = next(bno_reader)
        flight_ctr_idx = headers.index('flight_ctr')
        quat_x_idx = headers.index('quatX')
        quat_y_idx = headers.index('quatY')
        quat_z_idx = headers.index('quatZ')
        quat_w_idx = headers.index('quatW')
        checksum_idx = headers.index('Checksum Status')

        for row in bno_reader:
            if row[checksum_idx] == 'OK':
                bno_timestamps.append(row[flight_ctr_idx])
                quat_x.append(float(row[quat_x_idx]) / math.sqrt(1 - pow(float(row[quat_w_idx]), 2)))
                quat_y.append(float(row[quat_y_idx]) / math.sqrt(1 - pow(float(row[quat_w_idx]), 2)))
                quat_z.append(float(row[quat_z_idx]) / math.sqrt(1 - pow(float(row[quat_w_idx]), 2)))
                quat_w.append(float(row[quat_w_idx]))
                sum = (float(row[quat_w_idx]) * float(row[quat_w_idx])) + (float(row[quat_x_idx]) * float(row[quat_x_idx])) + (float(row[quat_y_idx]) * float(row[quat_y_idx])) + (float(row[quat_z_idx]) * float(row[quat_z_idx]))
                quat_sum_sq.append(sum)

        if not (len(bno_timestamps) == len(quat_x) == len(quat_y) == len(quat_z) == len(quat_w)):
            print("BNO quat and timestamp lists are different lengths!!")
            return 1
        else:
            print("BNO data read!")

    print("Accel length: ", len(accel_timestamps))
    print("BNO length: ", len(bno_timestamps))

    plotBno(quat_x, quat_y, quat_z, quat_w, bno_timestamps)

if __name__ == "__main__":
    main()