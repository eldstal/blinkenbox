from machine import Pin
from machine import ADC
from machine import PWM
import _thread

import time

print("Start")

LA = Pin(0, Pin.OUT)
CLK = Pin(1, Pin.OUT)
DATA = Pin(2, Pin.OUT)
OE = Pin(3, Pin.OUT)

# These are inverted (read as False when pressed)
BTN_PWR = Pin(14, Pin.IN, Pin.PULL_UP)
BTN_MODE = Pin(15, Pin.IN, Pin.PULL_UP)

#MIC = ADC(26)

# Output Enable is active low
OE_YES = False
OE_NO = True


REFRESH=0.001
INTENSITY=0




def clock():
    CLK.value(False)
    time.sleep(REFRESH)
    CLK.value(True)

def setup():
    OE.value(OE_YES)
    clock()


def flip():
    LA.value(True)
    time.sleep(REFRESH)
    LA.value(False)

def clear():
    print("Clearing!!")
    DATA.value(False)
    LA.value(False)
    for x in range(16*16):
      clock()
    flip()

def amplitude(ampl):
    for x in range(256):
        DATA.value(ampl < x)
        clock()
    flip()

def show():
    DATA.value(True)
    clock()

    for x in range(16):
        DATA.value(True)
        clock()
        flip()

def dim(level):
  level = min(level, 1.0)
  level = max(level, 0)

  print(f"Testing intensity {level}")

  duty = int((1-level) * 65536)
  DIMMER.init(freq=500, duty_u16=duty)



#DIMMER = PWM(OE, freq=500, duty_u16=0)
#dim(INTENSITY)

clear()
setup()


while True:
  for i in range(16):
    print("repetition!!")

    #while BTN_MODE.value() and BTN_PWR.value():
    #  pass

    # Early reset
    #if not BTN_PWR.value():
    #  break

    show()

  clear()

  #INTENSITY+=0.005
  #dim(INTENSITY)
