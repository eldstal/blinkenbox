
import fb
import snake
import time


fb = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

# A nice little gradient
for i in range(16):
    fb.set(i%16, i//16, i)

while True:
  time.sleep(1)

snake.main(fb)
