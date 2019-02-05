#!/usr/bin/env python3
########################################################################
# gears.py is used to handle the conversion and changing of gears
# from RPM to m/s and km/h
########################################################################


class gearcalc:

    def gearbox(a, b, RPM):

        chainring = [39, 52]
        sprocket = [27, 24, 22, 20, 18, 17, 16, 15, 14, 13, 12]

        wheel = 2.11  # circumference of wheels
        ratio = sprocket[b] / chainring[a]
        roll = wheel / ratio
        v = roll * RPM / 60 * 3.6
        return v
