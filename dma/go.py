
from machine import Pin

import time
import uctypes
import struct
import math
import rp_devices as devs

FRAMEBUF = bytearray(32)
FB_ADDR = uctypes.addressof(FRAMEBUF)

FAKE_PIO = bytearray(8)
FAKE_PIO_ADDR = uctypes.addressof(FAKE_PIO)


dma_chan = devs.DMA_CHANS[0]
dma = devs.DMA_DEVICE

dma_chan.READ_ADDR_REG = FB_ADDR
dma_chan.WRITE_ADDR_REG = FAKE_PIO_ADDR

dma_chan.TRANS_COUNT_REG = 1

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
dma_chan.CTRL_TRIG.DATA_SIZE=2    # One 32b word at a time
dma_chan.CTRL_TRIG.INCR_READ = 1  # Eat the buffer
dma_chan.CTRL_TRIG.INCR_WRITE = 0 # Only one target word
dma_chan.CTRL_TRIG.RING_SEL = 0 # Wrap the READ buf
dma_chan.CTRL_TRIG.RING_SIZE = int(math.log2(len(FRAMEBUF))) # Buffer size must be a power of two
dma_chan.CTRL_TRIG.IRQ_QUIET = 1
dma_chan.CTRL_TRIG.TREQ_SEL = 0x3F # Send fast as fuck
dma_chan.CTRL_TRIG.TREQ_SEL = 0x3F # Send fast as fuck
#dma_chan.CTRL_TRIG.TREQ_SEL = DREQ_PIO0_TX0 # Send only when the PIO is ready to receive


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
