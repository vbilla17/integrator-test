import matplotlib.pyplot as plt

def endBurnIndex(accel_timestamps, end_burn_time):
    end_idx = 0
    for i in range(0, len(accel_timestamps)):
        if accel_timestamps[i] < end_burn_time:
            end_idx = i
        else:
            break

    return end_idx

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