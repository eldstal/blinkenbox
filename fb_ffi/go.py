
import fb
import snake
import time
import math

import utime

# Taken from the micropython-usermod manual
# https://micropython-usermod.readthedocs.io/en/latest/usermods_12.html
def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func


fb = fb.Framebuf()

#fb.set(12,5,1)
#fb.flip()

fb.clear()
fb.flip()


intensities = [ x*16 for x in range(16) ]


@timed_function
def with_py_set(fb):
     # A pretty little gradient
  for x in range(len(intensities)):
    for y in range(0,16,2):
      fb._python_set(x, y, intensities[x])

    for y in range(1,16,2):
      fb._python_set(x, y, intensities[::-1][x])


@timed_function
def with_native_set(fb):
     # A pretty little gradient
  for x in range(len(intensities)):
    for y in range(0,16,2):
      fb._native_set(x, y, intensities[x])

    for y in range(1,16,2):
      fb._native_set(x, y, intensities[::-1][x])


@timed_function
def with_auto_set(fb):
     # A pretty little gradient
  for x in range(len(intensities)):
    for y in range(0,16,2):
      fb.set(x, y, intensities[x])

    for y in range(1,16,2):
      fb.set(x, y, intensities[::-1][x])


while True:
  with_py_set(fb)
  fb.flip()
  fb.clear()

  with_native_set(fb)
  fb.flip()
  fb.clear()

  with_auto_set(fb)
  fb.flip()
  fb.clear()

