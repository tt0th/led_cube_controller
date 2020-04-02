import time
from .animation import Animation
from ..led_cube_controller import LedCubeController, SIZE


class BillboardAnimation(Animation):
    def __init__(self):
        super().__init__()
        self.start_columns = [] + \
                             [[i, 0] for i in range(0, SIZE - 1)] + \
                             [[SIZE - 1, i] for i in range(0, SIZE - 1)] + \
                             [[i, SIZE - 1] for i in reversed(range(1, SIZE))] + \
                             [[0, i] for i in reversed(range(1, SIZE))]

        self.start_column_index = 0

    def animate(self, controller: LedCubeController):
        self.start_column_index = (self.start_column_index + 1) % len(self.start_columns)
        for i in range(SIZE):
            start_point = self.start_columns[self.start_column_index]
            controller.turn_on(start_point[0], start_point[1], i)

        time.sleep(0.05)
