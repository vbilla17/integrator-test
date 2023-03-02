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

        az, accel_timestamps = inputAccel(flight, sensor)
        gps_alt, gps_timestamps = inputGps(flight)
        baro_alt, baro_timestamps = inputBaro(flight)

        timescale = setTimescale(flight)

        az, accel_timestamps = trimData(az, accel_timestamps, timescale[0], timescale[1], timescale[2])
        gps_alt, gps_timestamps = trimData(gps_alt, gps_timestamps, timescale[0], timescale[1], timescale[2])
        baro_alt, baro_timestamps = trimData(baro_alt, baro_timestamps, timescale[0], timescale[1], timescale[2])

        correctAccel(az, flight, sensor)
        correctGps(gps_alt, flight)
        correctBaro(baro_alt)

        # velocities, altitudes = integrateAccel(gps_alt[0], az, accel_timestamps) # using trapezoidal integration
        velocities, altitudes = integrateAccelRungeKutta(gps_alt[0], az, accel_timestamps) # using runge kutta method

        printMaxes(az, velocities, altitudes, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps)

        makePlots(az, velocities, altitudes, accel_timestamps, gps_alt, gps_timestamps, baro_alt, baro_timestamps)
    else:
        print("ERROR: INVALID INPUT")
        return 1

if __name__ == "__main__":
    main()