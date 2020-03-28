import math
import time
import numpy as np
from transforms3d.derivations.eulerangles import x_rotation
from .animation import Animation
from ..led_cube_controller import LedCubeController


class CircleAnimation(Animation):
    def __init__(self):
        super().__init__()
        self.point = np.array([2, 2, 2])

    def animate(self, controller: LedCubeController):
        rotation_matrix = np.array(x_rotation(math.pi / 8))
        self.point = self.point.dot(rotation_matrix)
        controller.turn_on(self.point[0], self.point[1], self.point[2])
        time.sleep(0.5)
