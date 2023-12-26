#
# CircuitPython
#


import os
import sys
import time
import random



class Twinkle:
    def __init__(self, maxage=25):

        self.maxage = maxage

        # x, y, age
        self.stars = []
    
    def start(self):
        self.history = []
        self.gameover = False
        self.pos = ( random.randint(0, 15), random.randint(0, 15) )
        self.direction = random.randint(0, 3)

    def wrap(self, xy):
        x,y = xy
        return (x%16, y%16)
    
    def dist(self, xy1, xy2):
        x1,y1 = xy1
        x2,y2 = xy2

        return abs(y2-y1) + abs(x2-x1)
    
    def min_dist(self, xy):
        min_dist = 999999
        for sx,sy,_ in self.stars:
            dist = self.dist(xy, (sx,sy))
            min_dist = min(dist, min_dist)
        return min_dist
    
    def prune(self):
        self.stars = [ (x,y,age) for x,y,age in self.stars if age < self.maxage ]
    
    
    def step(self):
        self.stars = [ (x,y,age + 1) for x,y,age in self.stars ]
        self.prune()

    def star(self):
        for attempt in range(10):
            x,y = random.randint(0,15), random.randint(0,15)

            min_dist = self.min_dist((x,y))

            # If it's far enough away from other stars, it's good!
            if min_dist > 4:
                self.stars += [ (x, y, 0)]
                return



    def draw(self, display):

        display.clear()

        for x,y,age in self.stars:
            if age < 4:
                # Fresh stars get their twinkle at a cool angle
                twinkles = [
                               (-1, -1),
                               (-1,  1),
                               ( 1, -1),
                               ( 1,  1)
                              ]
            else:
                # Older stars have normal old regular twinkles
                twinkles = [
                               (0, -1),
                               (0,  1),
                               (-1, 0),
                               ( 1, 0)
                              ]
                
            for dx,dy in twinkles:
                tx = (x+dx) % 16
                ty = (y+dy) % 16

                intensity = int(64 - (70 * (age / self.maxage)))
                intensity = max(intensity, 0)

                display.px[ty][tx] += intensity
        
        # The star itself
        intensity = int(220 - (220 * (age / self.maxage)))
        intensity = max(intensity, 0)

        display.px[y][x] += intensity

        #display.blur()
        #display.glow()
        display.update()


def main(display):

    DEMO = Twinkle()
    DEMO.start()

    while True:

        DEMO.star()
        DEMO.draw(display)

        for frame in range(12):
            DEMO.step()
            DEMO.draw(display)
            time.sleep(0.05)


