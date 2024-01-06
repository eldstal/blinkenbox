#!/bin/env python3
# Test the menu in the comfort of your own terminal

# Terminal hacks stolen from stackoverflow, of course.

import time



from fakebuffer import FakeBuffer
import fontloader


if __name__ == "__main__":

    disp = FakeBuffer()

    font = fontloader.Font("fonts/3x5.fnt")

    step = font.width + font.spacing

    x = 0
    y = 0


    while True:
        x = 0
        y = 0

        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":

            disp.flip()
            font.draw(disp, x, y, c, 255)
            disp.flip()

            x += step

            if x+font.width > 15:
                x = 0
                y += font.height

            if y+font.height > 15:
                x = 0
                y = 0
                time.sleep(0.6)
                disp.clear()
                disp.flip()
                disp.clear()
                disp.flip()

            time.sleep(0.2)