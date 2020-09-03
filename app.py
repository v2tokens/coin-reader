from pathlib import Path
from shlex import split
from subprocess import run
from sys import exit

from requests import get
from RPi import GPIO as GPIO
from trio import open_nursery, run, sleep

NUM_PIN = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(NUM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

DEFAULT_PORT = 5000
TICKER_HOST = "ticker"
SCREEN1_HOST = "mbp-van-lotte"
SCREEN2_HOST = "scova"

counter = 0
COUNTER_GOAL = 30

should_sleep = False
SLEEP_FOR_SCREEN_ANIM = 10

TIP_TINY = Path("assets/sounds/tip_tiny.mp3").absolute()
TIP_GOAL = Path("assets/sounds/tip_medium.mp3").absolute()


def play_sound(fpath):
    try:
        run(split(f"play {fpath}"))
        return True
    except Exception:
        print(f"Unable to run 'play {fpath}'...")
        return False


def fire_request(url):
    try:
        get(url)
        return True
    except Exception:
        print(f"Failed to request {url}...")
        return False


def go_test():
    print("Running start-up tests...")
    for host in [TICKER_HOST, SCREEN1_HOST, SCREEN2_HOST]:
        success = fire_request(f"http://{host}:{DEFAULT_PORT}/ok")
        if not success:
            print(f"Unable to contact the '{host}' host, bailing out...")
            exit(1)
    print("Success...")


async def sleep_loop():
    global should_sleep

    while True:
        sleep_count = 0
        while should_sleep:
            if sleep_count == 0:
                print("Starting to sleep...")
            await sleep(1)
            sleep_count += 1
            if sleep_count == SLEEP_FOR_SCREEN_ANIM:
                print(f"Slept {SLEEP_FOR_SCREEN_ANIM} seconds...")
                should_sleep = False
        await sleep(0.1)


async def gpio_loop(nursery):
    global counter
    global should_sleep

    try:
        print("Running GPIO read loop...")
        while True:
            if GPIO.input(NUM_PIN) == 1:
                print("Coin detected...")

                play_sound(TIP_TINY)

                if not should_sleep:
                    print("Not sleeping, firing at screens...")
                    counter += 1
                    fire_request(f"http://{SCREEN1_HOST}:{DEFAULT_PORT}")
                    fire_request(f"http://{SCREEN2_HOST}:{DEFAULT_PORT}")

                if counter == COUNTER_GOAL and not should_sleep:
                    print("Goal reached...")
                    play_sound(TIP_GOAL)
                    fire_request(f"http://{TICKER_HOST}:{DEFAULT_PORT}")

                    print("Re-setting counter and flipping sleep bit...")
                    counter = 0
                    should_sleep = True

            await sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        nursery.cancel_scope.cancel()


async def main():
    go_test()

    async with open_nursery() as nursery:
        nursery.start_soon(gpio_loop, nursery)
        nursery.start_soon(sleep_loop)


run(main)
