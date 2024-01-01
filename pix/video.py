from fb import Framebuf
from file import fkopen
from time import sleep


"""
Display frekvensimages.
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
            self.fb.set(x, y, next(self.src)*255)
        self.fb.flip()
        

    def play(self):
        while True:
            self.next_frame()
            sleep(self.frametime)


if __name__ == "__main__":
    f = Framebuf()
    f.clear()
    f.flip()
    v = Video(fkopen("video.fk"), fb=f, framerate=15)
    v.play()
