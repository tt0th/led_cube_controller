import time
import RPi.GPIO as GPIO
from led_cube import SIZE

PIN_DISPLAY = 6
PIN_DATA = 19
PIN_CLOCK = 13


def setup():
    GPIO.setmode(GPIO.BCM)

    GPIO.setwarnings(False)
    GPIO.setup(PIN_DISPLAY, GPIO.OUT)
    GPIO.setup(PIN_DATA, GPIO.OUT)
    GPIO.setup(PIN_CLOCK, GPIO.OUT)
    GPIO.setwarnings(True)


def clear_cube():
    GPIO.output(PIN_DATA, GPIO.LOW)

    for _ in range(SIZE * (SIZE + 1)):
        GPIO.output(PIN_CLOCK, GPIO.HIGH)
        GPIO.output(PIN_CLOCK, GPIO.LOW)

    GPIO.output(PIN_DISPLAY, GPIO.HIGH)
    GPIO.output(PIN_DISPLAY, GPIO.LOW)


def start_outputting_cube_state(controller):
    GPIO.output(PIN_DISPLAY, GPIO.LOW)
    GPIO.output(PIN_DATA, GPIO.LOW)
    GPIO.output(PIN_CLOCK, GPIO.LOW)

    while True:
        # set all column
        for layer in range(SIZE):
            for i in range(SIZE):
                for j in range(SIZE):
                    GPIO.output(PIN_DATA, GPIO.HIGH if controller.is_on(i, j, layer) else GPIO.LOW)
                    GPIO.output(PIN_CLOCK, GPIO.HIGH)
                    GPIO.output(PIN_CLOCK, GPIO.LOW)

            # select layer
            for i in range(SIZE):
                GPIO.output(PIN_DATA, GPIO.HIGH if i == layer else GPIO.LOW)
                GPIO.output(PIN_CLOCK, GPIO.HIGH)
                GPIO.output(PIN_CLOCK, GPIO.LOW)

            # display settings
            GPIO.output(PIN_DISPLAY, GPIO.HIGH)
            GPIO.output(PIN_DISPLAY, GPIO.LOW)
            time.sleep(0.00001)
