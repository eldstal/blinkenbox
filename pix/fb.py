import matrix
import array
import uctypes
import micropython
import time

from machine import Timer
from machine import mem32

import rp_devices as devs


REMAP = [
    65535,    65508,    65479,    65451,    65422,    65394,    65365,    65337,
    65308,    65280,    65251,    65223,    65195,    65166,    65138,    65109,
    65081,    65052,    65024,    64995,    64967,    64938,    64909,    64878,
    64847,    64815,    64781,    64747,    64711,    64675,    64637,    64599,
    64559,    64518,    64476,    64433,    64389,    64344,    64297,    64249,
    64200,    64150,    64099,    64046,    63992,    63937,    63880,    63822,
    63763,    63702,    63640,    63577,    63512,    63446,    63379,    63310,
    63239,    63167,    63094,    63019,    62943,    62865,    62785,    62704,
    62621,    62537,    62451,    62364,    62275,    62184,    62092,    61998,
    61902,    61804,    61705,    61604,    61501,    61397,    61290,    61182,
    61072,    60961,    60847,    60732,    60614,    60495,    60374,    60251,
    60126,    59999,    59870,    59739,    59606,    59471,    59334,    59195,
    59053,    58910,    58765,    58618,    58468,    58316,    58163,    58007,
    57848,    57688,    57525,    57361,    57194,    57024,    56853,    56679,
    56503,    56324,    56143,    55960,    55774,    55586,    55396,    55203,
    55008,    54810,    54610,    54408,    54203,    53995,    53785,    53572,
    53357,    53140,    52919,    52696,    52471,    52243,    52012,    51778,
    51542,    51304,    51062,    50818,    50571,    50321,    50069,    49813,
    49555,    49295,    49031,    48764,    48495,    48223,    47948,    47670,
    47389,    47105,    46818,    46529,    46236,    45940,    45641,    45340,
    45035,    44727,    44416,    44102,    43785,    43465,    43142,    42815,
    42486,    42153,    41817,    41478,    41135,    40790,    40441,    40089,
    39733,    39375,    39013,    38647,    38279,    37907,    37531,    37153,
    36770,    36385,    35996,    35603,    35207,    34808,    34405,    33999,
    33589,    33175,    32758,    32338,    31913,    31486,    31054,    30619,
    30181,    29738,    29292,    28843,    28389,    27932,    27471,    27007,
    26539,    26066,    25590,    25111,    24627,    24140,    23649,    23153,
    22654,    22152,    21645,    21134,    20619,    20101,    19578,    19051,
    18521,    17986,    17447,    16905,    16358,    15807,    15252,    14693,
    14129,    13562,    12990,    12415,    11835,    11251,    10662,    10070,
    9473,     8872,     8266,     7657,     7043,     6424,     5802,     5175,
    4543,     3908,     3267,     2623,     1974,     1320,     662,      0 ]

class Framebuf:

  def __init__(self):
    self.frame_tim = Timer()
    self.dma_tim = Timer()

    self.matrix = matrix.matrix(brightness=0.2)
    
    # Depth (in image frames) of PWM modulation
    # Increase for better bit depth, but using more RAM (32B per frame)
    self.n_frames = 1

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


    #
    # Pixel mapping memo table
    # This maps an x/y of a pixel to the proper word and bit in one of the frame buffers
    #
    self.word_table = [ [ 0 for x in range(16) ] for y in range(16) ]
    self.bit_table = [ [ 0 for x in range(16) ] for y in range(16) ]
    for y in range(16):
      for x in range(16):
        self.word_table[y][x] = y//4 + (4 * (x >=8))
        self.bit_table[y][x] = (y%4)*8 + x%8
    


    # PWM bit patterns for a pixel at a given intensity
    # The first entry is the lowest intensity (off)
    # The last entry is the highest supported intensity (on)
    # Only the lowest n_frames bits will be used (and looped)
    self.pwm = array.array("L", [
        0x000000,
        0x000001,
        0x010101,
        0x050505,
        0x151515,
        0x313313,
        0x707077,
        0xFFFFFF,
    ])

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


  # Given an x/y coordinate of a pixel
  # returns the corresponding word index and bit index
  def set(self, x, y, intensity=255):

    pwm_bits = self.intensity_to_pwm(intensity)

    w = self.word_table[y][x]
    b = self.bit_table[y][x]
    
    for f in range(self.n_frames):
      word_addr = self.BACK_BUFFER + f*32 + w*4

      bit_value = ((pwm_bits >> f) & 1) << b

      mem32[word_addr] = mem32[word_addr] & ((1 << b) ^ 0xFFFFFFFF) | bit_value
        

  # Intensity is [0, 255]
  def slow_set(self, x, y, intensity=255):

    pwm_bits = self.intensity_to_pwm(intensity)

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

      if pwm_bits >> f & 1 == 1:
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

    dma_chan_main = 0
    dma_chan_trig = 1

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

