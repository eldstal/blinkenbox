#
# CircuitPython
#



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
        self.trail = []
        self.n_trails = 12
        self.trail_len = 10


    def new_trails(self):
        if len(self.trail) < self.n_trails:
            # x, y, trail color, speed
            self.trail.append((random.randint(0, 15), 0, random.randint(8, 85), random.random()*0.9 + 0.1))
   
    def step(self):
        # Move trails
        self.trail = [ (x, y+speed, color, speed) for x,y,color,speed in self.trail ]

        # Prune trails that have left the screen
        self.trail = [ (x, y, color, speed) for x,y,color,speed in self.trail if y < (16+self.trail_len)]

        self.new_trails()

        # Whichever trail has gotten further gets drawn last
        self.trail = list(sorted(self.trail, key=lambda tup: tup[1]))

    def draw(self, display):
        display.clear()

        for x,y,color,speed in self.trail:
            y = int(y)
            if y < 16:
                display.set(x, y, random.randint(32, 120))
            for yt in range(y-1, y-self.trail_len, -1):
                if 0 <= yt <= 16:
                    display.set(x, yt, color)

        display.flip()


GAME = None

def tick(display):
    global GAME
    
    if GAME is None:
        display.clear()

        GAME = Snake()
        GAME.start()


    GAME.step()
    GAME.draw(display)
    time.sleep(0.05)


