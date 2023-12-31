import matrix
import array
import uctypes
import micropython

from machine import Timer
from machine import mem32

import rp_devices as devs

# Native module!!
# Needs frame
try:
  import framebuddy
  HAVE_FRAMEBUDDY=True
except:
  print("------------")
  print("WARNING:")
  print("The native module framebuddy.mpy could not be loaded")
  print("fb.py will fall back to plain python pixel setting, and your graphics performance")
  print("will suffer greatly. Try uploading framebuddy.mpy to the board as well, it should")
  print("improve things a lot!")
  print("------------")
  HAVE_FRAMEBUDDY=False


class LED_MODE:
  PWM = 0,     # Duty cycle
  BCM32 = 1,   # Bit value, 5 bit depth
  BCM64 = 2,   # Bit value, 5 bit depth


class Framebuf:

  def __init__(self):
    self.frame_tim = Timer()
    self.dma_tim = Timer()

    self.matrix = matrix.matrix(brightness=0.1)
    
    # Depth (in image frames) of PWM modulation
    # Increase for better bit depth, but using more RAM (32B per frame)
    self.n_frames = 32

    self.buffer_a = bytearray(32*self.n_frames)
    self.FB_A_ADDR = uctypes.addressof(self.buffer_a)

    self.buffer_b = bytearray(32*self.n_frames)
    self.FB_B_ADDR = uctypes.addressof(self.buffer_b)


    # A pointer to the front buffer address,
    # which the trigger dma needs to copy to the main dma
    self.fb_ptr = bytearray(4)
    self.FRONT_BUFFER_PTR_ADDR = uctypes.addressof(self.fb_ptr)


    self.FRONT_BUFFER = self.FB_A_ADDR
    self.BACK_BUFFER = self.FB_B_ADDR
    mem32[self.FRONT_BUFFER_PTR_ADDR] = self.FRONT_BUFFER


    # PWM bit patterns for a pixel at a given intensity
    # The first entry is the lowest intensity (off)
    # The last entry is the highest supported intensity (on)
    # Only the lowest n_frames bits will be used (and looped)
    self.pwm = array.array("L", [
        0x00000000,
        0x00000001,
        0x01010101,
        0x05050505,
        0x15151515,
        0x13313313,
        0x70707077,
        0xFFFFFFFF,
    ])

    # Bit Code Modulation
    # For bits abcde, return a word of abbccccddddddddeeeeeeeeeeeeeeee
    self.bcm32 = array.array("L", [ 0 ]* 32)

    # Number of copies of each bit
    copies = [ 1, 2, 4, 8, 16 ]   # Expy
    for i in range(32):
      pattern = 0x0
      for bit_index in range(len(copies)-1,-1,-1):
        bit = (i >> bit_index) & 0x01

        for n in range(copies[bit_index]):
          pattern = (pattern << 1) | bit

      self.bcm32[i] = pattern
      #print(f"{i:02d} -> {pattern:>032b}")


    # Load the pattern mapping table into the native frame generator
    # This configures it to have all the grayscale levels we want!!
    if HAVE_FRAMEBUDDY:
      framebuddy.set_pattern_map(uctypes.addressof(self.bcm32), len(self.bcm32))
    

    self.dma_setup()

    # Push frames to PIO periodically
    self.start_auto_dma()


  def clear(self):
    for f in range(self.n_frames):
      for w in range(8):
        word_addr = self.BACK_BUFFER + f*32 + w*4
        mem32[word_addr] = 0


  # Intensity between 0 and 255 (integer)
  def intensity_to_pwm(self, intensity):

    # Range clamping [0,255]
    intensity = intensity & 0xFF

    n_steps = len(self.pwm)
    step = (intensity * n_steps) >> 8

    return self.pwm[step]
  

  # Intensity between 0 and 255 (integer)
  def intensity_to_bcm(self, intensity, mapping):

    # Range clamping [0,255]
    intensity = intensity & 0xFF

    n_steps = len(mapping)
    step = (intensity * n_steps) >> 8

    return mapping[step]

  def set(self, x, y, intensity=255):


    if HAVE_FRAMEBUDDY:
      self._native_set(x, y, intensity)
      return

    # Python fallback
    pixel_bits = self.intensity_to_bcm(intensity, self.bcm32)
    self._python_set(x, y, pixel_bits)

  # Intensity is [0, 255]
  def _native_set(self, x, y, pixel_bits=0xFF):

    framebuddy.transform_setbits(self.BACK_BUFFER, self.n_frames, x, y, pixel_bits)

  
  # Intensity is [0, 255]
  def _python_set(self, x, y, pixel_bits=0xFF):

    x = x & 0xF
    y = y & 0xF

    # Index into our framebuffer (word-width)
    w = 0

    # Right half of frame
    if (x >=8): w+=4

    # Vertical position
    w += y//4

    b = (y%4)*8 + x%8


    for f in range(self.n_frames):
      word_addr = self.BACK_BUFFER + f*32 + w*4

      if pixel_bits >> f & 1 == 1:
        mem32[word_addr] |= (1 << b)
      else:
        mem32[word_addr] &= (1 << b) ^ 0xFFFFFFFF


  def start_auto_dma(self):
    # Kick start the trigger_dma, which will start the main_dma frame pump
    # Once main_dma finishes one set of frames, the trigger_dma will restart etc etc etc
    self.trigger_dma_chan.M0_CTRL_TRIG.EN = 1   # Go!


  def flip(self):
    if self.FRONT_BUFFER == self.FB_A_ADDR:
      self.FRONT_BUFFER = self.FB_B_ADDR
      self.BACK_BUFFER = self.FB_A_ADDR
    else:
      self.FRONT_BUFFER = self.FB_A_ADDR
      self.BACK_BUFFER = self.FB_B_ADDR

    # Instruct the trigger DMA to start showing the new front buffer
    mem32[self.FRONT_BUFFER_PTR_ADDR] = self.FRONT_BUFFER
  
  def dma_setup(self):

    # Hardcoded to not interfere with the wifi driver
    # In Micropython 1.23, we'll be able to reserve an unused channel
    # in the correct way!
    dma_chan_main = 2
    dma_chan_trig = 3

    self.dma = devs.DMA_DEVICE
    self.main_dma_chan = devs.DMA_CHANS[dma_chan_main]
    self.trigger_dma_chan = devs.DMA_CHANS[dma_chan_trig]   # This is only used to trigger main_dma_chan


    #
    # main_dma, used to push pixel data to PIO
    #

    # The address of the register used to trigger the main dma
    # This is a pointer to M3_READ_ADDR_TRIG_REG
    #                                           channel                               mode   register
    self.main_dma_trigger_reg = devs.DMA_BASE + dma_chan_main * devs.DMA_CHAN_WIDTH + 0x30 + 0xC;

    self.main_dma_chan.M3_WRITE_ADDR_REG = devs.PIO0_TX

    # All the frames in one go!!
    self.main_dma_chan.M3_TRANS_COUNT_REG = 8 * self.n_frames

    self.main_dma_chan.M3_CTRL_REG = 0
    self.main_dma_chan.M3_CTRL.DATA_SIZE = 2  # One 32b word at a time
    self.main_dma_chan.M3_CTRL.INCR_READ = 1  # Eat the READ buffer
    self.main_dma_chan.M3_CTRL.INCR_WRITE = 0 # Only one target word
    self.main_dma_chan.M3_CTRL.RING_SEL = 0   # Wrap the READ buf

    # Ideally, we'd wrap on 32 bytes (ring_size=5), but the DMA controller goes craaaazy
    #self.dma_chan.CTRL.RING_SIZE = 5  # Wrap on 32 bytes (1 frame)
    self.main_dma_chan.M3_CTRL.RING_SIZE = 0  # Don't wrap. We just reset the source address each flip

    self.main_dma_chan.M3_CTRL.IRQ_QUIET = 1
    self.main_dma_chan.M3_CTRL.TREQ_SEL = devs.DREQ_PIO0_TX0 # Send only when the PIO is ready to receive

    self.main_dma_chan.M3_CTRL.CHAIN_TO = dma_chan_trig # On completion, start the trigger_dma

    self.main_dma_chan.M3_CTRL.EN = 1   # Enabled, but won't start just yet.


    #
    # trigger_dma, used to start main_dma every time it finishes
    #

    # The READ_ADDRESS register of mode3 of the main DMA
    # When this register is written, it will trigger the main DMA to perform another push of all frames to PIO.
    self.trigger_dma_chan.M0_WRITE_ADDR_REG = self.main_dma_trigger_reg

    # Copy the framebuffer address, so that the pixel push starts from there
    self.trigger_dma_chan.M0_READ_ADDR_REG = self.FRONT_BUFFER_PTR_ADDR

   # All the frames in one go!!
    self.trigger_dma_chan.M0_TRANS_COUNT_REG = 1

    self.trigger_dma_chan.M0_CTRL_TRIG_REG=0
    self.trigger_dma_chan.M0_CTRL_TRIG.DATA_SIZE=2    # One 32b word (the address register)
    self.trigger_dma_chan.M0_CTRL_TRIG.INCR_READ = 0  # Always read from the same place
    self.trigger_dma_chan.M0_CTRL_TRIG.INCR_WRITE = 0 # Always write to the same place
    self.trigger_dma_chan.M0_CTRL_TRIG.RING_SEL = 0   # Doesn't matter
    self.trigger_dma_chan.M0_CTRL_TRIG.RING_SIZE = 0  # Don't wrap.
    self.trigger_dma_chan.M0_CTRL_TRIG.IRQ_QUIET = 1  # No interrupts
    self.trigger_dma_chan.M0_CTRL_TRIG.TREQ_SEL = 0x3F    # as fast as fast can be
    self.trigger_dma_chan.M0_CTRL_TRIG.CHAIN_TO = dma_chan_trig  # Don't trigger any other channel

