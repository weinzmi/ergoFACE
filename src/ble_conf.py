#!/usr/bin/env python3

import serial
import time

"""
Simple parser for interfacing with the Waterrower S4 computer over a tty
on a Raspberry Pi.   This most-likely will work on other host computers
with some simple modification.
Information for the S4 proocol came from:
    Water Rower S4 & S5 USB Protocol
    Issue 1.04 - Aug 2009
"""


class S4State:
    CONNECTING = 1
    IDLE = 2


class S4Interface(object):
    def __init__(self):
        self.Reset()

    def DoIt(self):
        print("S4 INTERFACE  ---  DoIT")
        self.query_time = 1
        self.wheel_revolutions = 50
        self.rev_time = time.time()
        self.stroke_count = 100
        self.power = 250
        self.last_kcal = 12000
        self.first_kcal = 1  # flag for first time we get the kcal tally -
        # use the current value as a base
        self.last_stroke_time = time.time()

    def Exit(self):
        print("S4 INTERFACE  ---  EXIT")

    def Reset(self):
        print("S4 INTERFACE  ---  RESET")
        self.query_time = 1
        self.wheel_revolutions = 50
        self.rev_time = time.time()
        self.stroke_count = 100
        self.power = 150
        self.last_kcal = 12000
        self.first_kcal = 1  # flag for first time we get the kcal tally -
        # use the current value as a base
        self.last_stroke_time = time.time()

    def StartSerial(self):
        print("S4 INTERFACE  ---  Start Serial")

# Example of running this as a standalone test

# s4 = S4Interface()
# s4.DoIt()
