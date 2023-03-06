from integrator import *
from input_data import *
from correct_data import *
from print_data import *
from interpolator import *

def main():

    flight = input("Enter the flight name to plot: ").upper()
    sensor = input("Enter the sensor type to use (ADIS/ACCEL): ").upper()
    # integration_method = input()

    if isValidInput(flight, sensor):
        accel, accel_packets, accel_timestamps = inputAccel(flight, sensor) # accel = [[ax], [ay], [az]]
        gps_alt, gps_timestamps = inputGps(flight)
        baro_alt, baro_packets, baro_timestamps = inputBaro(flight)

        timescale = setTimescale(flight)

        accel, accel_timestamps = trimAccel(accel, accel_timestamps, timescale[0], timescale[1], timescale[2])
        gps_alt, gps_timestamps = trimData(gps_alt, gps_timestamps, timescale[0], timescale[1], timescale[2])
        baro_alt, baro_timestamps = trimData(baro_alt, baro_timestamps, timescale[0], timescale[1], timescale[2])

        correctAccel(accel, flight, sensor)
        correctGps(gps_alt, flight)
        correctBaro(baro_alt)

        # accel, accel_timestamps, baro_alt, baro_timestamps = interpolateAccel(accel, accel_timestamps, accel_packets, baro_alt, baro_timestamps, baro_packets)

        velocities_trap, altitudes_trap = integrateAccelTrap(gps_alt[0], accel[2], accel_timestamps) # using trapezoidal integration
        velocities_rk, altitudes_rk = integrateAccelRungeKutta(gps_alt[0], accel[2], accel_timestamps) # using runge kutta method

        printMaxes(accel, velocities_trap, altitudes_trap, velocities_rk, altitudes_rk, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps)

        makePlots(accel, velocities_trap, altitudes_trap, velocities_rk, altitudes_rk, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps)
    else:
        print("ERROR: INVALID INPUT")
        return 1

if __name__ == "__main__":
    main()