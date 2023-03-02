import math

def integrateAccel(start_alt, accel, accel_timestamps):
    last_accel = accel[0]
    last_timestamp = accel_timestamps[0]
    current_vel = 0
    current_alt = start_alt

    velocities = [0]  # initial velocity is 0
    altitudes = [current_alt]

    for i in range(1, len(accel_timestamps)):
        current_accel = accel[i]
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

def integrateAccelRungeKutta(start_alt, accel, accel_timestamps):
    last_accel = accel[0]
    last_timestamp = accel_timestamps[0]
    current_vel = 0
    current_alt = start_alt

    velocities = [0]  # initial velocity is 0
    altitudes = [current_alt]

    for i in range(1, len(accel_timestamps)):
        current_accel = accel[i]
        current_timestamp = accel_timestamps[i]
        delta_t = (current_timestamp - last_timestamp)

        # Using Runge-Kutta method
        k1 = delta_t * ((last_accel - gravVal(current_alt)))
        k2 = delta_t * ((last_accel + 0.5*k1) - gravVal(current_alt + 0.5*current_vel*delta_t))
        k3 = delta_t * ((last_accel + 0.5*k2) - gravVal(current_alt + 0.5*current_vel*delta_t))
        k4 = delta_t * ((last_accel + k3) - gravVal(current_alt + current_vel*delta_t))
        current_vel += (k1 + 2*k2 + 2*k3 + k4)/6

        last_accel = current_accel
        last_timestamp = current_timestamp
        velocities.append(current_vel)
        current_alt += delta_t * current_vel
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