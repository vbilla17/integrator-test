import csv
import matplotlib.pyplot as plt
import math

def interpolate(qx, qy, qz, qw, ax, ay, az, bno_packets, accel_packets, bno_timestamps, accel_timestamps):
    first_packet_num = int(min(bno_packets[0], accel_packets[0]))
    last_packet_num = int(max(bno_packets[-1], accel_packets[-1]))

    qx_interpolated = []
    qy_interpolated = []
    qz_interpolated = []
    qw_interpolated = []
    ax_interpolated = []
    ay_interpolated = []
    az_interpolated = []
    bno_timestamps_interpolated = []
    accel_timestamps_interpolated = []

    for i in range(first_packet_num, last_packet_num):
        print("<3 ")
        # check if the current packet number is in bno_packets
        if i in bno_packets:
            idx = bno_packets.index(i)
            qx_interpolated.append(qx[idx])
            qy_interpolated.append(qy[idx])
            qz_interpolated.append(qz[idx])
            qw_interpolated.append(qw[idx])
            bno_timestamps_interpolated.append(bno_timestamps[idx])
        else:
            if bno_timestamps_interpolated:
                qx_interpolated.append(qx_interpolated[idx - 1])
                qy_interpolated.append(qy_interpolated[idx - 1])
                qz_interpolated.append(qz_interpolated[idx - 1])
                qw_interpolated.append(qw_interpolated[idx - 1])
                bno_timestamps_interpolated.append(bno_timestamps[idx - 1])
            else:
                qx_interpolated.append(qx[0])
                qy_interpolated.append(qy[0])
                qz_interpolated.append(qz[0])
                qw_interpolated.append(qw[0])
                bno_timestamps_interpolated.append(bno_timestamps[0])

        # check if the current packet number is in accel_packets
        if i in accel_packets:
            idx = accel_packets.index(i)
            ax_interpolated.append(ax[idx])
            ay_interpolated.append(ay[idx])
            az_interpolated.append(az[idx])
            accel_timestamps_interpolated.append(accel_timestamps[idx])
        else:
            if accel_timestamps_interpolated:
                ax_interpolated.append(ax_interpolated[idx - 1])
                ay_interpolated.append(ay_interpolated[idx - 1])
                az_interpolated.append(az_interpolated[idx - 1])
                accel_timestamps_interpolated.append(accel_timestamps[idx - 1])
            else:
                ax_interpolated.append(ax[0])
                ay_interpolated.append(ay[0])
                az_interpolated.append(az[0])
                accel_timestamps_interpolated.append(accel_timestamps[0])

        if bno_timestamps_interpolated[-1] <= accel_timestamps_interpolated[-1]:
            bno_timestamps_interpolated[-1] = accel_timestamps_interpolated[-1]
        else:
            accel_timestamps_interpolated[-1] = bno_timestamps_interpolated[-1]

    return qx_interpolated, qy_interpolated, qz_interpolated, qw_interpolated, ax_interpolated, ay_interpolated, az_interpolated, bno_timestamps_interpolated, accel_timestamps_interpolated

def multiplyQuaternions(q1, q2):
    # q1q2
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([-x1*x2 - y1*y2 - z1*z2 + w1*w2,
                     x1*w2 + y1*z2 - z1*y2 + w1*x2,
                     -x1*z2 + y1*w2 + z1*x2 + w1*y2,
                     x1*y2 - y1*x2 + z1*w2 + w1*z2])

def transformAcc(qx,qy,qz,qw, acc_x, acc_y, acc_z):
    # Transform the accelerometer data into the world frame
    # qaq^-1
    q = [qw, qx, qy, qz]
    q_conj = [qw,-qx, -qy, -qz]
    a = [0, acc_x, acc_y, acc_z]

    # qaq^-1
    qaq_inv = multiplyQuaternions(multiplyQuaternions(q, a), q_conj)
    return qaq_inv[1:]

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
    ax.plot(acc_x, label='acc_x')
    ax.plot(acc_y, label='acc_y')
    ax.plot(acc_z, label='acc_z')

def main():
    accel_input_path = 'input/Jawbone/ACCEL-trimmed.csv'
    bno_input_path = 'input/Jawbone/BNO-trimmed.csv'

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
        packet_idx = headers.index('Packet #')

        for row in accel_reader:
            if row[checksum_idx] == 'OK':
                accel_timestamps.append(row[flight_ctr_idx])
                ax.append(float(row[ax_idx]))
                ay.append(float(row[ay_idx]))
                az.append(float(row[az_idx]))
                accel_packets.append(float(row[packet_idx]))

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
        packet_idx = headers.index('Packet #')

        for row in bno_reader:
            if row[checksum_idx] == 'OK':
                bno_timestamps.append(row[flight_ctr_idx])
                quat_x.append(float(row[quat_x_idx]))
                quat_y.append(float(row[quat_y_idx]))
                quat_z.append(float(row[quat_z_idx]))
                quat_w.append(float(row[quat_w_idx]))
                bno_packets.append(float(row[packet_idx]))
                # sum = (float(row[quat_w_idx]) * float(row[quat_w_idx])) + (float(row[quat_x_idx]) * float(row[quat_x_idx])) + (float(row[quat_y_idx]) * float(row[quat_y_idx])) + (float(row[quat_z_idx]) * float(row[quat_z_idx]))
                # quat_sum_sq.append(sum)

        if not (len(bno_timestamps) == len(quat_x) == len(quat_y) == len(quat_z) == len(quat_w)):
            print("BNO quat and timestamp lists are different lengths!!")
            return 1
        else:
            print("BNO data read!")

    print("Accel length: ", len(accel_timestamps))
    print("BNO length: ", len(bno_timestamps))

    plotBno(quat_x, quat_y, quat_z, quat_w, bno_timestamps)

    quat_x, quat_y, quat_z, quat_w, ax, ay, az, bno_timestamps, accel_timestamps = interpolate(quat_x, quat_y, quat_z, quat_w, ax, ay, az, bno_packets, accel_packets, bno_timestamps, accel_timestamps)

    print("Interpolated Accel length: ", len(accel_timestamps))
    print("Interpolated BNO length: ", len(bno_timestamps))

if __name__ == "__main__":
    main()