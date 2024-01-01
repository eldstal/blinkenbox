
import fb
import snake
import time


fb = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

fb.clear()
#fb.dma_flip()

# A nice little gradient
#for i in range(256):
#    fb.set(i%16, i//16, i)

#fb.dma_flip()

#while True:
#  time.sleep(1)

snake.main(fb)
