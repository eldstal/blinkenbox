
import fb
import snake
import time
import math


fb = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

fb.clear()
fb.flip()

intensities = [ x*16 for x in range(16) ]

# A nice little gradient
for x in range(len(intensities)):
  for y in range(0,16,2):
    fb.set(x, y, intensities[x])

  for y in range(1,16,2):
    fb.set(x, y, intensities[::-1][x])

fb.flip()

while True:
  time.sleep(1)

snake.main(fb)
