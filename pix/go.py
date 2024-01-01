
import fb
import snake
import time


fb = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

fb.clear()
#fb.dma_flip()

# A nice little gradient
#for x in range(16):
#  for y in range(16):
#    fb.set(x, y, x*16+y)

#fb.dma_flip()

#while True:
#  time.sleep(1)

snake.main(fb)
