#!/usr/bin/env python3

import time
from random import randint


"""
Simple parser for interfacing with the Waterrower S4 computer over a tty
on a Raspberry Pi.   This most-likely will work on other host computers
with some simple modification.
Information for the S4 proocol came from:
    Water Rower S4 & S5 USB Protocol
    Issue 1.04 - Aug 2009
"""


class bleState:
    CONNECTING = 1
    IDLE = 2


class bleValue(object):
    def __init__(self):
        self.Reset()

    def Transmit_csc(self):
        print("BLE VALUE  ---  CSC values")
        self.power = randint(100, 250)
        # this is an acumulated value and is devided by the ble client
        # witht the delta of the last revolution time
        self.wheel_revolutions = self.wheel_revolutions + 1
        self.rev_time = time.time()
        # this is an acumulated value and is devided by the ble client
        # witht the delta of the last stroke time
        self.stroke_count = self.stroke_count + 2
        self.last_stroke_time = time.time()

    def Transmit_cp(self):
        print("BLE VALUE  ---  CP values")
        self.power = randint(100, 250)
        # used different variables bacause they
        # are called twice in ble_gatt_server
        self.wheel_revolutions1 = self.wheel_revolutions1 + 1
        self.rev_time = time.time()
        self.stroke_count1 = self.stroke_count1 + 2
        self.last_stroke_time = time.time()

    def Exit(self):
        print("BLE VALUE  ---  EXIT")

    def Reset(self):
        print("BLE VALUE  ---  reset values")
        self.power = 0
        self.wheel_revolutions = 0
        self.rev_time = time.time()
        self.stroke_count = 0
        self.last_stroke_time = time.time()
        self.wheel_revolutions1 = 0
        self.stroke_count1 = 0

# Example of running this as a standalone test

# s4 = S4Interface()
# s4.Transmit()
