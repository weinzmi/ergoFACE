#!/usr/bin/env python3
########################################################################
# Filename    : BreathingLED.py
# Description : A breathing LED
# Author      : freenove
# modification: 2018/08/02
########################################################################
import RPi.GPIO as GPIO


class Ergopwm():

    def __init__(self, name, LedPin, mode):
        self.name = name
        self.LedPin = LedPin # 12 has to be defined in watt.py as a parameter
        self.mode = mode

        GPIO.setmode(self.mode)

        # Numbers GPIOs by physical location
        GPIO.setup(self.LedPin, GPIO.OUT)  # Set LedPin's mode is output
        GPIO.output(self.LedPin, GPIO.LOW)  # Set LedPin to low

        self.p = GPIO.PWM(self.LedPin, 1000)  # set Frequece to 1KHz
        self.p.start(0)  # Duty Cycle = 0

    def output(self, dc):
        GPIO.setmode(self.mode)
        GPIO.setup(self.LedPin, GPIO.OUT)
        self.p.ChangeDutyCycle(dc)  # Change duty cycle

    def destroy(self):
        GPIO.setmode(self.mode)
        GPIO.setup(self.LedPin, GPIO.OUT)  # Set LedPin's mode is output
        GPIO.output(self.LedPin, GPIO.LOW)
        self.p.stop()
        GPIO.output(self.LedPin, GPIO.LOW)  # turn off led
        GPIO.cleanup()
