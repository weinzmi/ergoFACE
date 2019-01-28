#!/usr/bin/env python3

import time
from random import randint


class bleValue(object):
    def __init__(self):
        self.Reset()

    def ftm_ib(self):
        print("BLE VALUE  ---  FTM Indoor Bike Data")
        self.speed = 30
        self.cadence = 90
        self.power = 250

    def ftm_status(self):
        print("BLE VALUE  ---  FTM Status")
        self.status = 0x04  # Fitness Machine Started or Resumed by the User

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
