#!/usr/bin/env python3
import rs232


class bleValue(object):
    def __init__(self):
        self.Reset()

    def ftm_ib(self):
        print("BLE VALUE - FTM Indoor Bike values")
        self.speed = rs232.Speed
        self.cadence = rs232.Cadence
        self.power = rs232.Power

    def ftm_status(self):
        print("BLE VALUE - FTM Status")
        self.status = 0x04  # Fitness Machine Started or Resumed by the User

    def Transmit_csc(self):
        if rs232.Speed > 0:
            print("BLE VALUE - Cycling Speed and Cadence values")
            self.power = rs232.Power
            # this is an acumulated value and is devided by the ble client
            # witht the delta of the last revolution time
            # in the script of andi, the speed and cadence are fixed, but the
            # delta time is variable, so this works as well
            # change fixed value "15" to variable for gear changes!!!
            self.gear = 15
            self.wheel_revolutions = rs232.Wheel_Rev
            self.rev_time = rs232.Wheel_LastEvTime
            self.stroke_count = rs232.Crank_Rev
            self.last_stroke_time = rs232.Crank_LastEvTime
        else:
            self.Reset()

    def Transmit_cp(self):
        if rs232.Speed > 0:
            print("BLE VALUE - Cycling Power Mesurement values")
            self.power = rs232.Power
            # used different variables bacause they
            # are called twice in ble_gatt_server
            # in the script of andi, the speed and cadence are fixed, but the
            # delta time is variable, so this works as well
            # change fixed value "15" to variable for gear changes!!!
            self.wheel_revolutions = rs232.Wheel_Rev
            self.rev_time = rs232.Wheel_LastEvTime
            # this is an acumulated value and is devided by the ble client
            # witht the delta of the last stroke time
            self.stroke_count = rs232.Crank_Rev
            self.last_stroke_time = rs232.Crank_LastEvTime
        else:
            self.Reset()

    def Exit(self):
        print("BLE VALUE - EXIT")

    def Reset(self):
        # print("BLE VALUE - reset all values to 0")
        self.rev_time = round(rs232.dT_s)
        self.last_stroke_time = round(rs232.dT_c)
        self.power = 0
        self.wheel_revolutions = 0
        self.stroke_count = 0
        self.revtime = 0
