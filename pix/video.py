from fb import Framebuf
from rle import inflate_rle
from time import sleep
from util import auto_rewind, fullbright


"""
Display rle images.
If multiple images are packed into a single file, they will be shown
in a looping animation.§
"""

class Video:
    def __init__(self, source, fb=None, framerate = 10):
        self.fb = fb or Framebuf()
        self.src = source
        self.frametime = 1/ framerate


    def next_frame(self):
        self.fb.clear()
        for i in range(256):
            y, x = divmod(i, 16)
            self.fb.set(x, y, next(self.src))
        self.fb.flip()
        

    def play(self):
        while True:
            self.next_frame()
            sleep(self.frametime)



if __name__ == "__main__":
    f = Framebuf()
    f.clear()
    f.flip()
    v = Video(fullbright(inflate_rle(auto_rewind("video"))), fb=f)
    v.play()
