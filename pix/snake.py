#
# CircuitPython
#


import os
import sys
import time
import random


LEFT = -1
RIGHT = 1
FORWARD = 0
N = 0
E = 1
S = 2
W = 3



class Snake:
    def __init__(self):
        self.history = []
    
    def start(self):
        self.history = []
        self.gameover = False
        self.pos = ( random.randint(0, 15), random.randint(0, 15) )
        self.direction = random.randint(0, 3)

    def wrap(self, xy):
        x,y = xy
        return (x%16, y%16)
    
    def move(self, xy, direction):
        x,y = xy
        if direction == N: return (x, y-1)
        if direction == S: return (x, y+1)
        if direction == E: return (x+1, y)
        return (x-1, y)

    def random_turn(self, old_dir):
        turn = random.choice( [LEFT]*1 + [FORWARD]*4 + [RIGHT]*1)
        new_dir = (old_dir + turn) % 4
        return new_dir
    
    def step(self):
        if self.gameover: return

        self.history.append(self.pos)
        self.pos = self.wrap(self.move(self.pos, self.direction))
        self.direction = self.random_turn(self.direction)

        if self.pos in self.history:
            self.gameover = True

    def draw(self, display):
        for x,y in self.history:
            display.set(x, y, 1)
        for x,y in [self.pos]:
            display.set(x, y, 1)

        display.flip()

        #display.push()
        #display.blur()
        #display.glow()
        #display.update()
        #display.pop()


def main(display):

    GAME = Snake()
    GAME.start()

    while True:
        GAME.step()
        GAME.draw(display)
        time.sleep(0.1)

        if GAME.gameover:
            GAME.start()
            display.clear()

