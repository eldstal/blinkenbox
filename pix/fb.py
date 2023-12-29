import matrix
import array

from machine import Timer

class Framebuf:

  def __init__(self):
    self.tim = []
    self.fb = []
    for x in range(4):
      self.tim.append(Timer())
      self.fb.append([0] * 8)
    self.matrix = matrix.matrix(brightness=0.10)
    self.flip()

  def clear(self):
    for x in range(4):
      for y in range(8):
        self.fb[x][y] = 0

  def set(self, x, y, v=1, intensity=15):

    x = x % 16
    y = y % 16

    # Index into wpx (word)
    w = 0

    # Right half of frame
    if (x >=8): w+=4

    # Vertical position
    w += y//4

    b = (y%4)*8 + x%8

    for x in range(4):
      if intensity >> x & 1 == 1:
        self.fb[x][w] |= (1 << b)
      else:
        self.fb[x][w] &= (1 << b) ^ 0xFFFFFFFF
    

  def flip(self):
    self.matrix.set_matrix(array.array("I", self.fb[0]))
    self.matrix.update()
    self.tim[0].init(period=1, mode=Timer.ONE_SHOT, callback=lambda t:self.push(1))
    self.tim[1].init(period=5, mode=Timer.ONE_SHOT, callback=lambda t:self.push(2))
    self.tim[2].init(period=10, mode=Timer.ONE_SHOT, callback=lambda t:self.push(3))
    self.tim[3].init(period=20, mode=Timer.ONE_SHOT, callback=lambda t:self.flip())
  
  def push(self, x):
    self.matrix.set_matrix(array.array("I", self.fb[x]))
    self.matrix.update()