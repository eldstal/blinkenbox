
import fb
import snake
import time
import math


disp = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

disp.clear()
disp.flip()

snake.main(disp)
