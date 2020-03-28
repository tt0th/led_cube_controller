import math
import time
import numpy as np
from transforms3d.derivations.angle_axes import angle_axis2mat
from .animation import Animation
from ..led_cube_controller import LedCubeController


class CircleAnimation(Animation):
    def __init__(self):
        super().__init__()
        self.point = np.array([6, 5, 1])
        self.rotation_matrix = np.array(angle_axis2mat(math.pi / 8, [1 / math.sqrt(3)] * 3))

    def animate(self, controller: LedCubeController):

        controller.turn_off(round(self.point[0]), round(self.point[1]), round(self.point[2]))
        self.point = self.point.dot(self.rotation_matrix)
        controller.turn_on(round(self.point[0]), round(self.point[1]), round(self.point[2]))

        time.sleep(0.1)
