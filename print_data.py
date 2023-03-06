import matplotlib.pyplot as plt

def endBurnIndex(accel_timestamps, end_burn_time):
    end_idx = 0
    for i in range(0, len(accel_timestamps)):
        if accel_timestamps[i] < end_burn_time:
            end_idx = i
        else:
            break

    return end_idx

def printMaxes(accel, velocities_trap, altitudes_trap, velocities_rk, altitudes_rk, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps):
    max_accel = max(accel[2][0:endBurnIndex(accel_timestamps, 15)])
    max_accel_g = max_accel * 0.031080950171567

    # print("Max Accel: ", max_accel_g, "g at ", accel_timestamps[accel[2].index(max_accel)], "s", "\n")
    print("Max Accel: {:.2f}g at {:.2f}s\n".format(max_accel_g, accel_timestamps[accel[2].index(max_accel)]))


    print("Max Integrated Velocity Trapezoid: {:.2f} at {:.2f}s".format(max(velocities_trap), accel_timestamps[velocities_trap.index(max(velocities_trap))]))
    print("Max Integrated Altitude Trapezoid: {:.2f} at {:.2f}s".format(max(altitudes_trap), accel_timestamps[altitudes_trap.index(max(altitudes_trap))]))

    print("Max Integrated Velocity Runge Kutta: {:.2f} at {:.2f}s".format(max(velocities_rk), accel_timestamps[velocities_rk.index(max(velocities_rk))]))
    print("Max Integrated Altitude Runge Kutta: {:.2f} at {:.2f}s".format(max(altitudes_rk), accel_timestamps[altitudes_rk.index(max(altitudes_rk))]))

    print("Max GPS Altitude: {:.2f} at {:.2f}s".format(max(gps_alt), gps_timestamps[gps_alt.index(max(gps_alt))]))
    print("Max Baro Altitude: {:.2f} at {:.2f}s".format(max(baro_alt), baro_timestamps[baro_alt.index(max(baro_alt))]))


def makePlots(accel, velocities_trap, altitudes_trap, velocities_rk, altitudes_rk, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps):
    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, accel[2])
    plt.title("Accel")

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, velocities_trap, label = "Trapezoidal")
    plt.plot(accel_timestamps, velocities_rk, label = "Runge Kutta")
    plt.title("Velocity")
    plt.legend()

    plt.figure(figsize=(10, 8))
    plt.plot(accel_timestamps, altitudes_trap, label = "Trapezoidal")
    plt.plot(accel_timestamps, altitudes_rk, label = "Runge Kutta")
    plt.plot(gps_timestamps, gps_alt, label = "GPS")
    plt.plot(baro_timestamps, baro_alt, label = "BARO")
    plt.title("Altitude")
    plt.legend()

    plt.show()