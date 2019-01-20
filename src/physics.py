########################################################################
# physics.py is used to handle physical watt calculation for SIM mode
# the basis for this was found here:
# https://johnedevans.wordpress.com/2018/05/31/the-physics-of-zwift-cycling/
########################################################################

import math


class CyclingEquationOfMotion:

    # Variables
    mRider = 80  # mass in kg of the rider
    mBike = 7  # mass in kg of the bike
    M = mBike + mRider  # mass in kg of the bike + rider
    h = 1.92  # hight in m of rider
    A = 0.0276 * h**0.725 * mRider**0.425 + 0.1647
    # cross sectional area of the rider, bike and wheels
    Crr = 0.3386 / M  # coefficient of rolling resistance
    v = gear * RPM  # velocity in m/s

    # Constants
    g = 9.8067  # acceleration in m/s^2 due to gravity
    p = 1.225  # air density in kg/m^3 at 15°C at sea level
    CD = 0.725  # coefficient of drag
    E = 1  # drive chain efficiency

    # inputs
    G =  # gradiant in %
    gear =  # gear factor for RPM of DAUM
    RPM =  # RPM from DAUM

    # output
    P = E * (M * g * v * cos(arctan(G)) * Crr + M * g * v * sin(arctan(G))
             + 1/2*p * CD * A * v**3)
