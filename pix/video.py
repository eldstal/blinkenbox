from fb import Framebuf
from rle import inflate_rle
from time import sleep


"""
Display rle images.
If multiple images are packed into a single file, they will be shown
in a looping animation.§
"""


def display(buf, data, framerate=10):
    """unpack image and write to display"""
    if framerate:
        frametime = 1/framerate
    while True:
        for i, b in enumerate(inflate_rle(data)):
            y = (i // 16)
            x = i % 16
            buf.set(x, y, int(b>0))
            if y % 16 == 0 and x == 0:
                buf.flip()
                if framerate:
                    sleep(frametime)
                    buf.clear()
                else:
                    return
    


if __name__ == "__main__":
    f = Framebuf()
    f.clear()
    f.flip()
    with open("video", "rb") as img:
        data = img.read()
    display(buf, data)
