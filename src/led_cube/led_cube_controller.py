from .led_cube import SIZE


class LedCubeController:
    _pixels = [[[0] * SIZE for _ in range(SIZE)] for _ in range(SIZE)]

    def turn(self, x, y, z, value):
        if 0 <= x <= (SIZE - 1) and 0 <= y <= (SIZE - 1) and 0 <= z <= (SIZE - 1):
            self._pixels[x][y][z] = value

    def turn_on(self, x, y, z):
        self.turn(x, y, z, 1)

    def turn_off(self, x, y, z):
        self.turn(x, y, z, 0)

    def is_on(self, x, y, z):
        if 0 <= x <= (SIZE - 1) and 0 <= y <= (SIZE - 1) and 0 <= z <= (SIZE - 1):
            return self._pixels[x][y][z]
        else:
            return 0

    def is_off(self, x, y, z):
        if 0 <= x <= (SIZE - 1) and 0 <= y <= (SIZE - 1) and 0 <= z <= (SIZE - 1):
            return not self._pixels[x][y][z]
        else:
            return 0

    def clear_pixels(self):
        for i in range(SIZE):
            for j in range(SIZE):
                for k in range(SIZE):
                    self.turn_off(i, j, k)
