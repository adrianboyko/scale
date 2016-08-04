#!/usr/bin/env python3

import RPi.GPIO as gpio
import time

MAGNET_PIN = 4
LASER_PIN = 14

gpio.setmode(gpio.BCM)

gpio.setup(MAGNET_PIN, gpio.OUT)
gpio.setup(LASER_PIN, gpio.OUT)

gpio.output(MAGNET_PIN, False)
gpio.output(LASER_PIN, True)

print("lon, loff, mon, moff, pwm")

while True:
    cmd = input("Command: ")

    if cmd == "lon":
        gpio.output(LASER_PIN, True)

    if cmd == "loff":
        gpio.output(LASER_PIN, False)

    if cmd == "mon":
        gpio.output(MAGNET_PIN, True)

    if cmd == "moff":
        gpio.output(MAGNET_PIN, False)

    if cmd == "pwm":
        p = gpio.PWM(MAGNET_PIN, 10)
        p.start(10)
        time.sleep(2)	
        p.stop()
