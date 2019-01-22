import gpxpy
import gpxpy.gpx
import gpxpy.geo as mod_geo
import time
import math
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys


def module_load():

    global fileName
    global fileList
    global dirName
    global cnt

    dirName = "GPX/"
    items = sorted(os.listdir(dirName))

    fileList = []
    # get list of yaml files in directory
    for names in items:
        if names.endswith(".gpx"):
            fileList.append(names)
    cnt = 0
    # output the list of yaml files
    print("gpx ------------ found GPX files")
    for fileName in fileList:
        sys.stdout.write("[%d] %s\n\r" % (cnt, fileName))
        cnt = cnt + 1

    # select per index the watt program
    # issue#5 - error handling in watt.py module load
    fileName = get_user_input()
    print("gpx ------------ selected File:\n\r", fileList[fileName])
    f = open(dirName + fileList[fileName])
    f.close()


def get_user_input():

    while True:
        try:
            return int(input("\n\rgpx ------------ Select watt program [0 - "
                             + str(cnt - 1) + "]: "))

        except ValueError:
            print("gpx ------------ Invalid input. Please try again!")


def gpx_run():

    gpx_file = open(dirName + fileList[fileName], 'r')
    gpx = gpxpy.parse(gpx_file)

    length = gpx.length_3d()
    print('Distance: %s' % length)

    # this is simly removing all points with no change in 3m
    gpx.reduce_points(2000, min_distance=3)
    # smoothin both
    gpx.smooth(vertical=True, horizontal=True)
    # and again smoothing just vertical
    gpx.smooth(vertical=True, horizontal=False)

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

    # datafild for calculation and plotting
    df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time',
                               'dist', 'ele', 'grad', 'pow'])

    for track in gpx.tracks:
        for segment in track.segments:
            for point_no, point in enumerate(segment.points):
                # print the current point information from GPX file
                # print('Point at ({0},{1}) -> {2} -> {3}'
                #       .format(point.latitude,
                #               point.longitude,
                #               point.elevation,
                #               point.time))
                # calculate the distance between two point in 3D
                distance = mod_geo.distance(point.latitude,
                                            point.longitude,
                                            point.elevation,
                                            segment.points[point_no - 1].latitude,
                                            segment.points[point_no - 1].longitude,
                                            segment.points[point_no - 1].elevation)

                # calculate the elevation between points
                elevation = point.elevation - segment.points[point_no - 1].elevation

                # avoid division by 0
                if distance == 0:
                    gradient = 0
                else:
                    # calculate gradient between points
                    gradient = elevation / distance * 100

                # test with simulated velocity of 20km/h == 5.55 m/s
                v = 5.55

                # inputs for power calculation
                G = gradient/100

                # output of power calculation
                P = E * (M * g * v * math.cos(math.atan(G)) * Crr + M * g * v
                         * math.sin(math.atan(G)) + 1/2*p * CD * A * v**3)

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

                # load gpx information into a datafild for calculation and plotting

                df = df.append({'lon': point.longitude,
                                'lat': point.latitude,
                                'alt': point.elevation,
                                'time': point.time,
                                'dist': distance,
                                'ele': elevation,
                                'grad': gradient,
                                'pow': P},
                               ignore_index=True)

                # time.sleep(wait)

    # start of plotting
    def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    fig, host = plt.subplots()
    fig.subplots_adjust(right=0.75)

    par1 = host.twinx()
    par2 = host.twinx()

    # Offset the right spine of par2.  The ticks and label have already been
    # placed on the right by twinx above.
    par2.spines["right"].set_position(("axes", 1.2))
    # Having been created by twinx, par2 has its frame off, so the line of its
    # detached spine is invisible.  First, activate the frame but make the patch
    # and spines invisible.
    make_patch_spines_invisible(par2)
    # Second, show the right spine.
    par2.spines["right"].set_visible(True)

    p1, = host.plot(df['time'], df['alt'], "b-", label="Altitude")
    p2, = par1.plot(df['time'], df['ele'], "r-", label="Elevation")
    p3, = par2.plot(df['time'], df['pow'], "g-", label="Power")

    # host.set_xlim(0, 2)
    # host.set_ylim(0, 2)
    # par1.set_ylim(0, 4)
    # par2.set_ylim(1, 65)

    host.set_xlabel("Time")
    host.set_ylabel("Altitude")
    par1.set_ylabel("Elevation")
    par2.set_ylabel("Power")

    host.yaxis.label.set_color(p1.get_color())
    par1.yaxis.label.set_color(p2.get_color())
    par2.yaxis.label.set_color(p3.get_color())

    tkw = dict(size=4, width=1.5)
    host.tick_params(axis='y', colors=p1.get_color(), **tkw)
    par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
    par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
    host.tick_params(axis='x', **tkw)

    lines = [p1, p2, p3]

    host.legend(lines, [l.get_label() for l in lines])

    plt.show()

    for index, row in df.iterrows():
        print("Gradient:  ", f"{row['grad']:4.2f}", "%", "Power:   ",
              f"{row['pow']:4.2f}", "W")

        wait = row['dist'] / v

        print("Wait:      ", f"{wait:4.2f}", "s")

        time.sleep(wait)


module_load()
gpx_run()
