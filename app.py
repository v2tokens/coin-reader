import time
from pathlib import Path
from shlex import split
from subprocess import run
from sys import exit

from requests import get
from RPi import GPIO as GPIO

NUM_PIN = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(NUM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

DEFAULT_PORT = 5000
TICKER_HOST = "ticker"
SCREEN1_HOST = "mbp-van-lotte"
SCREEN2_HOST = "ilinx"

counter = 0
COUNTER_GOAL = 5

SLEEP_FOR_SCREEN_ANIM = 30

TIP_TINY = Path("assets/sounds/tip_tiny.mp3").absolute()
TIP_GOAL = Path("assets/sounds/tip_medium.mp3").absolute()


def play_sound(fpath):
    time.sleep(2)
    run(split(f"play {fpath}"))


def fire_request(url):
    try:
        get(url)
        return True
    except Exception:
        print(f"Failed to request {url}...")
        return False


def go_test():
    for host in [TICKER_HOST, SCREEN1_HOST, SCREEN2_HOST]:
        success = fire_request(f"http://{host}:{DEFAULT_PORT}/ok")
        if not success:
            print(f"Unable to contact the '{host}' host, bailing out...")
            exit(1)


print("Running start-up tests...")
go_test()
print("Success!")

try:
    print("Running GPIO read loop...")
    while 1:
        if GPIO.input(NUM_PIN) == 1:
            print("Coin detected...")

            play_sound(TIP_TINY)
            fire_request(f"http://{SCREEN1_HOST}:{DEFAULT_PORT}")
            fire_request(f"http://{SCREEN2_HOST}:{DEFAULT_PORT}")

            counter += 1
            if counter == COUNTER_GOAL:
                print("Goal reached...")
                play_sound(TIP_GOAL)
                fire_request(f"http://{TICKER_HOST}:{DEFAULT_PORT}")
                counter = 0

                print(f"Going to sleep for {SLEEP_FOR_SCREEN_ANIM} seconds...")
                time.sleep(SLEEP_FOR_SCREEN_ANIM)
                print("Waking up again...")

        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
