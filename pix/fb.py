
import matrix
import array

class Framebuf:

  def __init__(self):
    self.wpx = [ 0 ]*8
    self.matrix = matrix.matrix(lumen=0.05)

  def clear(self):
    self.wpx = [ 0 ]*8

  def set(self, x, y, v=1):

    x = x % 16
    y = y % 16

    # Index into wpx (word)
    w = 0

    # Right half of frame
    if (x >=8): w+=4

    # Vertical position
    w += y//4

    b = (y%4)*8 + x%8

    if (v):
      self.wpx[w] |= (1 << b)
    else:
      self.wpx[w] &= (1 << b) ^ 0xFFFFFFFF

  def flip(self):
    self.matrix.set_matrix(array.array("I", self.wpx))
    #self.matrix.set_matrix(self.wpx)
    self.matrix.update()
