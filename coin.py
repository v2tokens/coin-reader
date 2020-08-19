import time

from requests import get
from RPi import GPIO as GPIO

NUM_PIN = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(NUM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while 1:
    if GPIO.input(NUM_PIN) == 0:
        # TODO(decentral1se): use dns local hostnames and also
        #                     have these pluggable in case they change
        get("http://10.0.1.180:5000")  # currently the led
        get("http://10.0.1.100:5000")  # currently the gui
    time.sleep(0.1)

GPIO.cleanup()
