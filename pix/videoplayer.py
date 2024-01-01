import video

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
        self._buf[y*16 + x] = pixel
        

if __name__ == "__main__":
    import sys
    import file
    if not 2 <= len(sys.argv) <= 3:
        sys.exit(f"usage: {sys.argv[0]} video.fk [framerate=15]")


    framerate = 10
    if len(sys.argv) == 3:
        framerate = int(sys.argv[2])
    
    f = FakeBuffer()


    vid = file.fkopen(sys.argv[1], brightness_hack=True)
    
    v = video.Video(vid, f, framerate)

    try:
        v.play()
    except KeyboardInterrupt:
        print("\n"*15)

