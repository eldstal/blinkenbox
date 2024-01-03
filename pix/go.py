
import fb
import snake
import time
import math


disp = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

disp.clear()
disp.flip()

intensities = [ x*16 for x in range(16) ]

def gradients():
  while True:

    # A nice little gradient
    for x in range(64):
      disp.set((x)%16, (x)//16, x*4, fb.LED_MODE.BCM64)

    disp.flip()

def swell(intensities):
    for i in intensities:
      for y in range(5):
        for x in range(7):
          disp.set(x, y, i)
      disp.flip()
      disp.clear()



  
  #if mode == fb.LED_MODE.PWM:
  #  mode = fb.LED_MODE.BCM
  #else:
  #  mode = fb.LED_MODE.PWM

while True:
  #gradients()
  swell(range(256))
  swell(range(255,-1,-1))

snake.main(disp)
