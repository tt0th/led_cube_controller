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

    ARROW = [
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    ]

    EMARSYS = [
        [0, 0, 0, 0, 1, 1],
        [0, 0, 1, 1, 0, 0],
        [1, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1],
        [0, 0, 1, 1, 0, 0]
    ]

    CROWN = [
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    PICTURE = CROWN

    def animate(self, controller: LedCubeController):
        self.clear_relevant_columns(controller)

        self.move_index_forward()

        for layer in range(len(self.PICTURE)):
            for i in range(len(self.PICTURE[0])):
                start_point = self.start_columns[self.index_with_offset(i)]
                if self.PICTURE[layer][i] == 1:
                    controller.turn_on(start_point[0], start_point[1], layer)

        time.sleep(0.1)

    def move_index_forward(self):
        self.start_column_index = self.index_with_offset(1)

    def index_with_offset(self, offset):
        return (self.start_column_index + offset) % len(self.start_columns)

    def clear_relevant_columns(self, controller: LedCubeController):
        for i in range(SIZE):
            for j in range(len(self.start_columns)):
                start_point = self.start_columns[j]
                controller.turn_off(start_point[0], start_point[1], i)
