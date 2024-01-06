from math import ceil

brightness = " ·+o0@"

def get_pixel(value):
    v = ceil((value/255)*(len(brightness)-1))
    return brightness[v]


class FakeBuffer:
    """
        Fake framebuffer for testing
    """

    def __init__(self):
        self._buf = [0]*256

    def _draw(self, buf):
        out = []
        for i, pixel in enumerate(buf):
            if i and i % 16 == 0:
                out.append("\n")
            out.append(get_pixel(pixel))
        return "".join(out)

    def flip(self):
        print(self._draw(self._buf), end="\033[15A\r")

    def clear(self):
        self._buf = [0]*256

    def set(self, x, y, pixel):
        if x < 16 and y < 16:
            self._buf[y*16 + x] = pixel


if __name__ == "__main__":
  disp = FakeBuffer()
  for i in range(16):
    disp.set(i, i, 16*i)
  disp.flip()

