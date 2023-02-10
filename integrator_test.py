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
    bno_timestamps_interpolated = []
    accel_timestamps_interpolated = []

    for i in range(first_packet_num, last_packet_num + 1):
        # check if the current packet number is in bno_packets
        if i in bno_packets:
            idx = bno_packets.index(i)
            qx_interpolated.append(qx[idx])
            qy_interpolated.append(qy[idx])
            qz_interpolated.append(qz[idx])
            qw_interpolated.append(qw[idx])
            bno_timestamps_interpolated.append(i)

        # check if the current packet number is in accel_packets
        if i in accel_packets:
            idx = accel_packets.index(i)
            ax_interpolated.append(ax[idx])
            ay_interpolated.append(ay[idx])
            az_interpolated.append(az[idx])
            accel_timestamps_interpolated.append(i)

        # use the latest value from either bno or accel until a new value arrives
        else:
            if bno_timestamps_interpolated:
                qx_interpolated.append(qx_interpolated[-1])
                qy_interpolated.append(qy_interpolated[-1])
                qz_interpolated.append(qz_interpolated[-1])
                qw_interpolated.append(qw_interpolated[-1])
                bno_timestamps_interpolated.append(i)
            if accel_timestamps_interpolated:
                ax_interpolated.append(ax_interpolated[-1])
                ay_interpolated.append(ay_interpolated[-1])
                az_interpolated.append(az_interpolated[-1])
                accel_timestamps_interpolated.append(i)

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
 
 '''
 @param quat_XYZ array that contains all the quaternians during flight
 @param accel_XYZ array that contains all the acceleration data during flight
 @return allWorldAccels is type array containing vectors of world-centric accleration data
 allQuats = [
    quat_XYZ_timestamp0 = [x0, y0, z0],
    quat_XYZ_timestamp1 = [x1, y1, z1]
    ...
    quant_XYZ_timestampN = [xN, yN, zN]
 ]

 allAccels = [

 ]
 '''

 def transformAllAcc(allQuats, allAccles):
    allWorldAccels = []
    for i in range len(allQuats):
        allWorldAccels.append(transformAcc(allQuats[i][0], allQuats[i][1], allQuats[i][2], \
                        allAccels[i][0], allAccels[i][1], allAccels[i][2]) \
                        )
    return allWorldAccels


'''
Integrates allAccelData using corresponding timestamps (dx) in accel_timestamps

allAccelData = [
    accel_timestamp0 = [x, y, z],
    accel_timestamp1 = [x, y, z],
    ...
    accel_timestampN = [x, y, z]
]

accel_timestamp = [
    time0,
    time1,
    ...
    timeN
]
'''
def integrate(allAccelData, accel_timestamp):
    # array of instantaneous velocity at each timestamp
    vels = []
    
    for i in range(0, len(allAccelData) - 1):
        #inst_vel is the instantaneous velocity between the two timestamps
        inst_vel = [0,0,0]

        inst_vel[0] += 0.5 * (accel_timestamp[i+1] - accel_timestamp[i]) * \
                        (allAccelData[i][0] + allAccelData[i+1][0])

        inst_vel[1] += 0.5 * (accel_timestamp[i+1] - accel_timestamp[i]) * \
                        (allAccelData[i][1] + allAccelData[i+1][1])

        inst_vel[2] += 0.5 * (accel_timestamp[i+1] - accel_timestamp[i]) * \
                        (allAccelData[i][2] + allAccelData[i+1][2])
        vels.append(inst_vel)

    return vels

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

    # // convert each of the quaternian one component arrays 
    # into an array of quaternian objects represented by a length 3 vector
    # this is basically typename quaternian allQuatData[]
    '''
    changing the format from
    quant_x = [
        scalar0,
        scalar1,
        ...
        scalarN
    ]
    
    to

    allQuatData = [
        quat_timestamp0 = [x, y, z],
        quat_timestamp1 = [x, y, z],
        ...
        quat_timestampN = [x, y, z]
]
    '''
    allQuatData = []
    allAccellData = []
    for i in range len(quat_x):
        allQuatData.append([quat_x[i], quat_y[i], quat_z[i]])
        allAccelData.append([ax[i], ay[i], az[i]])

    integrate(transformAllAcc(allQuatData, allAccelData))

if __name__ == "__main__":
    main()