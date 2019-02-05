import gpxpy
import gpxpy.gpx
import gpxpy.geo as mod_geo
import time
import math

# Parsing an existing file:
# -------------------------

gpx_file = open('GPX/Morning_Ride_short.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

# Variables for power calculation
mRider = 80  # mass in kg of the rider
mBike = 7  # mass in kg of the bike
M = mBike + mRider  # mass in kg of the bike + rider
h = 1.92  # hight in m of rider
A = 0.0276 * h**0.725 * mRider**0.425 + 0.1647
# cross sectional area of the rider, bike and wheels
Crr = 0.3386 / M  # coefficient of rolling resistance
# v = gear * RPM  # velocity in m/s

# Constants
g = 9.8067  # acceleration in m/s^2 due to gravity
p = 1.225  # air density in kg/m^3 at 15°C at sea level
CD = 0.725  # coefficient of drag
E = 1  # drive chain efficiency

for track in gpx.tracks:
    for segment in track.segments:
        for point_no, point in enumerate(segment.points):
            # print the current point information from GPX file
            print('Point at ({0},{1}) -> {2} -> {3}'
                  .format(point.latitude,
                          point.longitude,
                          point.elevation,
                          point.time))
            # calculate the distance between two point in 3D
            distance = mod_geo.distance(point.latitude,
                                        point.longitude,
                                        point.elevation,
                                        segment.points[point_no - 1].latitude,
                                        segment.points[point_no - 1].longitude,
                                        segment.points[point_no - 1].elevation)
            print("Distance:  ", f"{distance:4.2f}", "m")

            # calculate the elevation between points
            elevation = point.elevation - segment.points[point_no - 1].elevation
            print("Elevation: ", f"{elevation:4.2f}", "m")

            # avoid division by 0
            if distance == 0:
                gradient = 0
            else:
                # calculate gradient between points
                gradient = elevation / distance * 100

            print("Gradient:  ", f"{gradient:4.2f}", "%")

            # test with simulated velocity of 20km/h == 5.55 m/s
            v = 5.55

            # inputs for power calculation
            G = gradient/100

            # output of power calculation
            P = E * (M * g * v * math.cos(math.atan(G)) * Crr + M * g * v
                     * math.sin(math.atan(G)) + 1/2*p * CD * A * v**3)

            print("Power:   ", f"{P:4.2f}", "W")

            """
            the simulation is close to the calculator found here:
            https://www.gribble.org/cycling/power_v_speed.html

            gpx.py:
            Gradient:   3.00 %
            Power:   194.46 W
            gribble.org:
            Gradient:   3.00 %
            Power:   194.82 W

            """
            # this is the procesing time for each point to point (segment)
            # but what if the speed (RPM) changes in between this time?
            # this will not work, but good for simulation with constant speed
            # another for loop will be neccesarry with a sleep of 1sec for
            # recalculation of dynamic sleep time based on
            # the refreshed velocity

            wait = distance / v
            print("Wait:      ", f"{wait:4.2f}", "s")

            time.sleep(wait)
