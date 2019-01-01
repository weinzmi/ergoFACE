#!/usr/bin/env python3
########################################################################
# Filename    : Alertor.py
# Description : Alarm by button.
# Author      : freenove
# modification: 2018/08/02
########################################################################
import RPi.GPIO as GPIO
import time
import math

buzzerPin = 11  # define the buzzerPin


def setup():
    global p
    print('Program is starting...')
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(buzzerPin, GPIO.OUT)  # Set buzzerPin's mode is output

    p = GPIO.PWM(buzzerPin, 1)
    p.start(0);


def loop():
    alertor()
    print('buzzer on ...')


def alertor():
    p.start(5)

    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(2349)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(1975)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(1760)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(1975)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(1760)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(1567)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(2349)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(1975)  # output PWM
    time.sleep(0.25)
    p.ChangeFrequency(2093)  # output PWM

    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(2349)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(1975)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(1760)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(1975)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(1760)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(1567)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(2349)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(2093)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(1975)  # output PWM
    time.sleep(0.125)
    p.ChangeFrequency(2093)  # output PWM

def stopAlertor():
    p.stop()


def destroy():
    GPIO.output(buzzerPin, GPIO.LOW)  # buzzer off
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

