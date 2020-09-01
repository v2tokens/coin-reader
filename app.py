import time

from requests import get
from RPi import GPIO as GPIO

NUM_PIN = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(NUM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

TICKER_URL = "http://ticker:5000"
SCREEN1_URL = "http://MBP-van-Lotte:5000"
SCREEN2_URL = "http://screen2:5000"

counter = 0
COUNTER_GOAL = 30

try:
    while 1:
        if GPIO.input(NUM_PIN) == 0:
            get(SCREEN1_URL)
            get(SCREEN2_URL)
            counter += 1
            if counter == COUNTER_GOAL:
                get(TICKER_URL)
                counter = 0
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
