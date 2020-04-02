import time
import signal
import sys
import threading
import random
import math
from led_cube.led_cube import SIZE
from led_cube.led_cube_protocol import clear_cube, setup, start_outputting_cube_state
from led_cube.led_cube_controller import LedCubeController
from led_cube.animations.animation import Animation
# from led_cube.animations.circle import CircleAnimation


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    clear_cube()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class SnowThread(Animation):

    def animate(self, controller: LedCubeController):
        for i in range(SIZE):
            for j in range(SIZE):
                for k in reversed(range(SIZE - 1)):
                    if controller.is_on(i, j, k):
                        controller.turn_off(i, j, k)
                        controller.turn_on(i, j, k + 1)

        controller.turn_on(random.randint(0, SIZE - 1), random.randint(0, SIZE - 1), 0)

        time.sleep(0.1)


class WaveThread(Animation):
    def __init__(self):
        super().__init__()
        self.mid_point_height = 0
        self.mid_point_velocity = 0

    def mid_point_acceleration(self):
        return 0.5 if self.mid_point_height <= 3.5 else -0.5

    def animate(self, controller: LedCubeController):
        max_distance = math.sqrt(3.5 ** 2 + 3.5 ** 2)

        controller.clear_pixels()

        for i in range(SIZE):
            for j in range(SIZE):
                distance_from_mid = math.sqrt((3.5 - i) ** 2 + (3.5 - j) ** 2)
                k = 3.5 + ((max_distance - distance_from_mid) / max_distance) * (self.mid_point_height - 3.5)
                k = round(k)
                if 0 <= k <= (SIZE - 1):
                    controller.turn_on(i, j, k)

        self.mid_point_height = self.mid_point_height + self.mid_point_velocity
        self.mid_point_velocity = self.mid_point_velocity + self.mid_point_acceleration()
        time.sleep(0.1)


class SphereThread(Animation):
    def __init__(self):
        super().__init__()
        self.radius = 0

    MAX_RADIUS = 6

    def update_pixels(self, controller: LedCubeController):
        for i in range(SIZE):
            for j in range(SIZE):
                for k in range(SIZE):
                    if math.sqrt((3.5 - i) ** 2 + (3.5 - j) ** 2 + (3.5 - k) ** 2) < self.radius:
                        controller.turn_on(i, j, k)
                    else:
                        controller.turn_off(i, j, k)

    def animate(self, controller: LedCubeController):
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
        self.position = [random.randint(0, SIZE - 1), random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)]
        self.velocity = [random.randint(0, SIZE - 1) / 8, random.randint(0, SIZE - 1) / 8,
                         random.randint(0, SIZE - 1) / 8]

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
        if self.position[i] > (SIZE - 1):
            self.position[i] = SIZE - 1
            self.velocity[i] = -self.velocity[i]


class MovingPointsThread(Animation):
    def __init__(self):
        super().__init__()
        self.points = [
            MovingPoint(), MovingPoint(), MovingPoint(), MovingPoint(), MovingPoint(), MovingPoint()
        ]

    def animate(self, controller: LedCubeController):
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


class PlanesThread(Animation):
    def __init__(self):
        super().__init__()
        self.i = 0
        self.d = 1

    def animate(self, controller: LedCubeController):
        for i in range(SIZE):
            for j in range(SIZE):
                for k in range(SIZE):
                    if i == self.i or j == self.i or k == self.i:
                        controller.turn_on(i, j, k)
                    else:
                        controller.turn_off(i, j, k)

        self.i = self.i + self.d

        if self.i < 0:
            self.i = 0
            self.d = 1

        if self.i > (SIZE - 1):
            self.i = SIZE - 1
            self.d = -1

        time.sleep(0.2)


class ThreadThread(threading.Thread):
    def __init__(self, controller: LedCubeController):
        threading.Thread.__init__(self, daemon=True)
        self.controller = controller

    def run(self):
        while True:
            # self.run_with_timeout(CircleAnimation())
            self.run_with_timeout(SnowThread())
            self.run_with_timeout(WaveThread())
            self.run_with_timeout(SphereThread())
            self.run_with_timeout(MovingPointsThread())
            self.run_with_timeout(PlanesThread())

    def run_with_timeout(self, animation):
        started = time.time()
        while (time.time() - started) < 20:
            animation.animate(self.controller)


controller = LedCubeController()

ThreadThread(controller).start()

setup()
start_outputting_cube_state(controller)
