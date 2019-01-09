#!/usr/bin/env python3
########################################################################
# pwm.py is used to set and output the PWM signal on GPIO
########################################################################
import RPi.GPIO as GPIO


class Ergopwm:

    LedPin = 12

    def setup(self):
        global p
        GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
        GPIO.setup(self.LedPin, GPIO.OUT)  # Set LedPin's mode is output
        GPIO.output(self.LedPin, GPIO.LOW)  # Set LedPin to low

        self.p = GPIO.PWM(self.LedPin, 61.5)  # set Frequece to 61.5 Hz
        self.p.start(0)  # Duty Cycle = 0

    def output(self, dc):
        self.p.ChangeDutyCycle(dc)  # Change duty cycle

    def stop(self):
        self.p.stop()
        GPIO.output(self.LedPin, GPIO.LOW)  # turn off led

    def destroy(self):
        self.p.stop()
        GPIO.output(self.LedPin, GPIO.LOW)  # turn off led
        GPIO.cleanup()
