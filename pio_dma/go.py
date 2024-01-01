
from machine import Pin

import time
import uctypes
import struct
import math
import array
import rp_devices as devs

from matrix import matrix
MAT = matrix(brightness=0.35)

#import matrix_old
#matrix_old.start()


FRAMEBUF = array.array("b", [0]*32)
FRAMEBUF_ADDR = uctypes.addressof(FRAMEBUF)

#FAKE_PIO = bytearray(8)
#FAKE_PIO_ADDR = uctypes.addressof(FAKE_PIO)


dma_chan = devs.DMA_CHANS[0]
dma = devs.DMA_DEVICE

dma_chan.READ_ADDR_REG = FRAMEBUF_ADDR
#dma_chan.WRITE_ADDR_REG = FAKE_PIO_ADDR
dma_chan.WRITE_ADDR_REG = devs.PIO0_TX

#dma_chan.TRANS_COUNT_REG = len(FRAMEBUF) // 4   # One frame per xfer
dma_chan.TRANS_COUNT_REG = 8

def hard_clear():
  for w in range(8):
    px = 0x00000000
    machine.mem32[devs.PIO0_TX] = px

def flip():

  while dma_chan.CTRL_TRIG.BUSY:
    time.sleep(0.01)

  # CTRL register:
  # Read 32 bits at a time
  # INCR_WRITE = 0 (always write to the same address)
  # INCR_READ = 1
  # DATA_SIZE = 2 (word)
  # RING_SEL = 0 (loop read)
  # RING_SIZE = log2(FRAMEBUF_SIZE)
  # 
  # Now: TREQ 0x3F for full fucking speeeed
  # Later: Write only when DREQ_PIO0_TX0

  dma_chan.CTRL_TRIG_REG=0
  dma_chan.READ_ADDR_REG = FRAMEBUF_ADDR
  dma_chan.CTRL_TRIG.DATA_SIZE=2    # One 32b word at a time
  dma_chan.CTRL_TRIG.INCR_READ = 1  # Eat the buffer
  #dma_chan.CTRL_TRIG.INCR_READ = 0  # Don't Eat the buffer
  dma_chan.CTRL_TRIG.INCR_WRITE = 0 # Only one target word
  dma_chan.CTRL_TRIG.RING_SEL = 0 # Wrap the READ buf
  #dma_chan.CTRL_TRIG.RING_SIZE = int(math.log2(len(FRAMEBUF))) # Buffer size must be a power of two
  #dma_chan.CTRL_TRIG.RING_SIZE = 5 # Probably correct, according to legend
  dma_chan.CTRL_TRIG.RING_SIZE = 0  # But wrapping at 32 bytes doesn't work, so we just start the transfer manually. Whatever.

  dma_chan.CTRL_TRIG.IRQ_QUIET = 1
  #dma_chan.CTRL_TRIG.TREQ_SEL = 0x3F # Send fast as fuck
  dma_chan.CTRL_TRIG.TREQ_SEL = devs.DREQ_PIO0_TX0 # Send only when the PIO is ready to receive

  dma_chan.CTRL_TRIG.EN = 1   # Go go go go go

  #while dma_chan.CTRL_TRIG.BUSY:
  #  time.sleep(0.01)

  #dma_chan.CTRL_TRIG.EN = 0   # Stop stop stop stop

  #print("Framebuffer transmitted!!")

def manual_flip():
  for i in range(8):
    flip()
  #time.sleep(0.1)


def dma_test():
  for i in range(32):
    FRAMEBUF[i] = 0xA0 + i

  for i in range(8):
    FAKE_PIO[i] = 0

  print(f"Output before DMA triggered: {FAKE_PIO}")

  for xfer in range(10):
    dma_chan.CTRL_TRIG.EN = 1   # Go go go go go

    while dma_chan.CTRL_TRIG.BUSY:
      time.sleep(0.1)

    print(f"Output after DMA completed: {FAKE_PIO}")


  while True:
    time.sleep(1)

def dump_fb():
    for a in range(FRAMEBUF_ADDR, FRAMEBUF_ADDR+32, 4):
      w = machine.mem32[a]
      print(f"{w:08x}")

#MAT.clear()
#MAT.update()

hard_clear()

for i in range(len(FRAMEBUF)):
  FRAMEBUF[i] = i % 256
  #FRAMEBUF[i] = 0xFF
#FRAMEBUF[0] = 0x0F

#for i in range(len(FRAMEBUF)//2):
#  FRAMEBUF[i] = 0

#for w in range(8):
#  data = 0xFFFFFF00 + w
#  machine.mem32[FRAMEBUF_ADDR] = data
#  time.sleep(0.05)


idx = 0

flip()
dump_fb()

while True:
  flip()
  FRAMEBUF[idx] += 1
  #if (idx == 1): dump_fb()
  FRAMEBUF[16+idx] -= 1
  idx = (idx + 1) % 16
  #time.sleep(0.05)

while True:
  # One full manual frame
  for W in range(8):
    px = 0x55555555
    machine.mem32[devs.PIO0_TX] = px

  time.sleep(0.1)

  # One full manual frame
  for W in range(8):
    px = 0xAAAAAAAA
    machine.mem32[devs.PIO0_TX] = px

  time.sleep(0.1)

#flip()
#time.sleep(0.3)
#flip()
#time.sleep(0.3)
#flip()
#time.sleep(10)
#time.sleep(10)
#flip()
#time.sleep(10)
#flip()
#flip()

while True:

  #for w in range(8):
  #  data = 0xFFFFFF00 + w
  #  machine.mem32[devs.PIO0_TX] = data
  #  time.sleep(0.05)

  time.sleep(0.5)
