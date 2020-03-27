import RPi.GPIO as GPIO
import time
import signal
import sys
import threading
import random
import math

PIN_DISPLAY = 6
PIN_DATA = 19
PIN_CLOCK = 13

N = 8


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')

    GPIO.output(PIN_DATA, GPIO.LOW)
    for _ in range(N * (N + 1)):
        GPIO.output(PIN_CLOCK, GPIO.HIGH)
        GPIO.output(PIN_CLOCK, GPIO.LOW)

    GPIO.output(PIN_DISPLAY, GPIO.HIGH)
    GPIO.output(PIN_DISPLAY, GPIO.LOW)

    # GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def empty_cube_state():
    return [[[0] * N for _ in range(N)] for _ in range(N)]


# global 3D array to hold state
pixels = empty_cube_state()


# 00 01 02 03 04 05 06 07
# 10 11 12 13 14 15 16 17
# 20 21 22 23 24 25 26 27
# 30 31 32 33 34 35 36 37
# 40 41 42 43 44 45 46 47
# 50 51 52 53 54 55 56 57
# 60 61 62 63 64 65 66 67
# 70 71 72 73 74 75 76 77


class LedCubeController:
    def turn(self, x, y, z, value):
        if 0 <= x <= 7 and 0 <= y <= 7 and 0 <= z <= 7:
            pixels[x][y][z] = value

    def turn_on(self, x, y, z):
        self.turn(x, y, z, 1)

    def turn_off(self, x, y, z):
        self.turn(x, y, z, 0)

    def is_on(self, x, y, z):
        if 0 <= x <= 7 and 0 <= y <= 7 and 0 <= z <= 7:
            return pixels[x][y][z]
        else:
            return 0

    def is_off(self, x, y, z):
        if 0 <= x <= 7 and 0 <= y <= 7 and 0 <= z <= 7:
            return not pixels[x][y][z]
        else:
            return 0

    def clear_pixels(self):
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    self.turn_off(i, j, k)


class StoppableThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.stopped = False

    def stop(self):
        self.stopped = True

    def stoppable_run(self, controller: LedCubeController):
        pass

    def run(self):
        controller = LedCubeController()
        while not self.stopped:
            self.stoppable_run(controller)


class SnowThread(StoppableThread):

    def stoppable_run(self, controller: LedCubeController):
        for i in range(N):
            for j in range(N):
                for k in reversed(range(N - 1)):
                    if controller.is_on(i, j, k):
                        controller.turn_off(i, j, k)
                        controller.turn_on(i, j, k + 1)

        controller.turn_on(random.randint(0, N - 1), random.randint(0, N - 1), 0)

        time.sleep(0.1)


class WaveThread(StoppableThread):
    def __init__(self):
        super().__init__()
        self.mid_point_height = 0
        self.mid_point_velocity = 0

    def mid_point_acceleration(self):
        return 0.5 if self.mid_point_height <= 3.5 else -0.5

    def stoppable_run(self, controller: LedCubeController):
        max_distance = math.sqrt(3.5 ** 2 + 3.5 ** 2)

        controller.clear_pixels()

        for i in range(N):
            for j in range(N):
                distance_from_mid = math.sqrt((3.5 - i) ** 2 + (3.5 - j) ** 2)
                k = 3.5 + ((max_distance - distance_from_mid) / max_distance) * (self.mid_point_height - 3.5)
                k = round(k)
                if 0 <= k <= 7:
                    controller.turn_on(i, j, k)

        self.mid_point_height = self.mid_point_height + self.mid_point_velocity
        self.mid_point_velocity = self.mid_point_velocity + self.mid_point_acceleration()
        time.sleep(0.1)


class SphereThread(StoppableThread):
    def __init__(self):
        super().__init__()
        self.radius = 0

    MAX_RADIUS = 6

    def update_pixels(self, controller: LedCubeController):
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    if math.sqrt((3.5 - i) ** 2 + (3.5 - j) ** 2 + (3.5 - k) ** 2) < self.radius:
                        controller.turn_on(i, j, k)
                    else:
                        controller.turn_off(i, j, k)

    def stoppable_run(self, controller: LedCubeController):
        while self.radius < self.MAX_RADIUS:
            self.radius = self.radius + 0.5
            self.update_pixels(controller)
            time.sleep(0.1)

        while self.radius > 0:
            self.radius = self.radius - 0.5
            self.update_pixels(controller)
            time.sleep(0.1)


class MovingPoint:

    def __init__(self):
        self.position = [random.randint(0, N - 1), random.randint(0, N - 1), random.randint(0, N - 1)]
        self.velocity = [random.randint(0, N - 1) / 8, random.randint(0, N - 1) / 8, random.randint(0, N - 1) / 8]

    def x_int(self):
        return round(self.position[0])

    def y_int(self):
        return round(self.position[1])

    def z_int(self):
        return round(self.position[2])

    def move(self):
        self._move_dimension(0)
        self._move_dimension(1)
        self._move_dimension(2)

    def _move_dimension(self, i):
        self.position[i] = self.position[i] + self.velocity[i]
        if self.position[i] < 0:
            self.position[i] = 0
            self.velocity[i] = -self.velocity[i]
        if self.position[i] > 7:
            self.position[i] = 7
            self.velocity[i] = -self.velocity[i]


class MovingPointsThread(StoppableThread):
    def __init__(self):
        super().__init__()
        self.points = [
            MovingPoint(), MovingPoint(), MovingPoint(), MovingPoint(), MovingPoint(), MovingPoint()
        ]

    def stoppable_run(self, controller: LedCubeController):
        controller.clear_pixels()
        for p in self.points:
            controller.turn_on(math.floor(p.position[0]), math.floor(p.position[1]), math.floor(p.position[2]))
            controller.turn_on(math.floor(p.position[0]), math.floor(p.position[1]), math.ceil(p.position[2]))
            controller.turn_on(math.floor(p.position[0]), math.ceil(p.position[1]), math.floor(p.position[2]))
            controller.turn_on(math.floor(p.position[0]), math.ceil(p.position[1]), math.ceil(p.position[2]))
            controller.turn_on(math.ceil(p.position[0]), math.floor(p.position[1]), math.floor(p.position[2]))
            controller.turn_on(math.ceil(p.position[0]), math.floor(p.position[1]), math.ceil(p.position[2]))
            controller.turn_on(math.ceil(p.position[0]), math.ceil(p.position[1]), math.floor(p.position[2]))
            controller.turn_on(math.ceil(p.position[0]), math.ceil(p.position[1]), math.ceil(p.position[2]))
            p.move()
        time.sleep(0.1)


class PlanesThread(StoppableThread):
    def __init__(self):
        super().__init__()
        self.i = 0
        self.d = 1

    def stoppable_run(self, controller: LedCubeController):
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    if i == self.i or j == self.i or k == self.i:
                        controller.turn_on(i, j, k)
                    else:
                        controller.turn_off(i, j, k)

        self.i = self.i + self.d

        if self.i < 0:
            self.i = 0
            self.d = 1

        if self.i > 7:
            self.i = 7
            self.d = -1

        time.sleep(0.2)


class ThreadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        while True:
            thread = SnowThread()

            thread.start()
            time.sleep(10)
            thread.stop()

            thread = WaveThread()
            thread.start()
            time.sleep(10)
            thread.stop()

            thread = SphereThread()
            thread.start()
            time.sleep(10)
            thread.stop()

            thread = MovingPointsThread()
            thread.start()
            time.sleep(10)
            thread.stop()

            thread = PlanesThread()
            thread.start()
            time.sleep(10)
            thread.stop()


ThreadThread().start()

# setup
GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)
GPIO.setup(PIN_DISPLAY, GPIO.OUT)
GPIO.setup(PIN_DATA, GPIO.OUT)
GPIO.setup(PIN_CLOCK, GPIO.OUT)
GPIO.setwarnings(True)


def change_output(pin, value):
    GPIO.output(pin, value)


change_output(PIN_DISPLAY, GPIO.LOW)
change_output(PIN_DATA, GPIO.LOW)
change_output(PIN_CLOCK, GPIO.LOW)

while True:
    # set all column
    for layer in range(N):
        for i in range(N):
            for j in range(N):
                GPIO.output(PIN_DATA, GPIO.HIGH if pixels[i][j][layer] == 1 else GPIO.LOW)
                GPIO.output(PIN_CLOCK, GPIO.HIGH)
                GPIO.output(PIN_CLOCK, GPIO.LOW)

        # select layer
        for i in range(N):
            change_output(PIN_DATA, GPIO.HIGH if i == layer else GPIO.LOW)
            change_output(PIN_CLOCK, GPIO.HIGH)
            change_output(PIN_CLOCK, GPIO.LOW)

        # display settings
        change_output(PIN_DISPLAY, GPIO.HIGH)
        change_output(PIN_DISPLAY, GPIO.LOW)
        time.sleep(0.00001)
