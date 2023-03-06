import math
import matplotlib.pyplot as plt

def latGravSurface(lat):
        # Cache sine squared of latitude bc we use it twice
        latSinSquare = math.pow(math.sin(lat*math.pi), 2)
        ge = 9.7803267715   # Equatorial gravity
        return ge*( (1 + 0.001931851353*latSinSquare)/ math.sqrt(1 - 0.0066943800229*latSinSquare))

def gravVal(lat, h):
    mToFt = 3.28084
    a = 6378.137    # Equatorial radius [km]
    b = 6356.7523   # Polar radius [km]
    gSurf = latGravSurface(lat)
    sinLat = math.sin(lat*math.pi)
    cosLat = math.cos(lat*math.pi)
    rActual = math.sqrt( (math.pow(a*a*cosLat, 2) + math.pow(b*b*sinLat, 2))/ ( math.pow(a*cosLat, 2) + math.pow(b*sinLat,2)) ) # Earth radius at given latitude
    # Return gravity in ft/s^2
    return gSurf*mToFt*math.pow( (rActual*1000*mToFt)/(h + rActual*1000*mToFt), 2 )

def gravValEstimate(lat, h):
    return (9.780318) * (1 + 0.0053024 * math.sin(lat)**2 + 0.0000058 * math.sin(2 * lat)**2) - 3.086 * 10**-6 * h

def magicNumbers(lat, h):
    mToFt = 3.28084
    a = 6378.137    # Equatorial radius [km]
    b = 6356.7523

    latSinSquare = math.pow(math.sin(lat*math.pi), 2)
    ge = 9.7803267715   # Equatorial gravity

    gSurf = ge*( (1 + 0.001931851353*latSinSquare)/ math.sqrt(1 - 0.0066943800229*latSinSquare))
    # print("{:.6f}".format(gSurf))

    sinLat = math.sin(lat*math.pi)
    cosLat = math.cos(lat*math.pi)

    rActual = math.sqrt( (math.pow(a*a*cosLat, 2) + math.pow(b*b*sinLat, 2))/ ( math.pow(a*cosLat, 2) + math.pow(b*sinLat,2)) ) # Earth radius at given latitude
    

    9.821031*3.28084*math.pow( (6361.366692*1000*3.28084)/(h + 6361.366692*1000*3.28084), 2 )


def main():
    alt_min = 0
    alt_max = 250000
    interval = 1000

    altitudes = [x * interval for x in range(alt_min, alt_max)]

    lat = 35.3467755

    gravs_wgs = [gravVal(lat, alt) for alt in altitudes]
    gravs_est = [gravValEstimate(lat, alt) for alt in altitudes]
    gravs_magic = [magicNumbers(lat, alt) for alt in altitudes]

    plt.figure(figsize=(10, 8))
    plt.plot(altitudes, gravs_magic, label = "Magic Numbers")
    # plt.plot(altitudes, gravs_wgs, label = "WGS84 Calcs")
    # plt.plot(altitudes, gravs_est, label = "Estimated")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
