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

    self.matrix = matrix.matrix(brightness=0.30)
    
    # Depth (in image frames) of PWM modulation
    # Increase for better bit depth, but using more RAM (32B per frame)
    self.n_frames = 8

    self.fb = bytearray(32*self.n_frames)
    self.FRAME_BASE_ADDR = uctypes.addressof(self.fb)

    # A pointer to the frame address,
    # which the trigger dma needs to copy to the main dma
    self.fb_ptr = bytearray(4)
    self.FRAME_BASE_PTR_ADDR = uctypes.addressof(self.fb_ptr)
    mem32[self.FRAME_BASE_PTR_ADDR] = self.FRAME_BASE_ADDR
    
    #self.start()
    #self.flip_phase = 0
    #self.bit_depth = 4
    #self.set_frame(0)

    
    


    # PWM bit patterns for a pixel at a given intensity
    # The first entry is the lowest intensity (off)
    # The last entry is the highest supported intensity (on)
    # Only the lowest n_frames bits will be used (and looped)
    self.pwm = array.array("L", [
        0x00,   # 0/8
        0x10,   # 1/8
        0x11,   # 2/8
        0x91,   # 3/8
        0x55,   # 4/8
        0x5B,   # 5/8
        0x77,   # 6/8
        0x7F,   # 7/8
        0xFF,   # 8/8
    ])


    # tick -> frame number to show
    self.intervals = array.array("L",[
      1,
      2,
      4,
      8,
      16,
      32,

      64,
      128
    ])

    self.dma_setup()

    # Push frames to PIO periodically
    self.start_auto_dma()

    # Swap framebuffer at set intervals
    #self.autoflip()

  def clear(self):
    for f in range(self.n_frames):
      for w in range(8):
        #self.fb[f][w] = 0
        word_addr = self.FRAME_BASE_ADDR + f*32 + w*4
        mem32[word_addr] = 0

  def remap_intensity(self, intensity):

    imax = 2**self.bit_depth

    intensity = min(intensity, imax)

    #norm_intensity = intensity
    # Rescale to 0...255
    norm_intensity = int(256 * intensity / imax)

    norm_intensity = max(0, norm_intensity)
    norm_intensity = min(255, norm_intensity)

    # Use the LUT to delinearize the color curve
    mapped_intensity = REMAP[norm_intensity]
    mapped_intensity = 0xFFFF - mapped_intensity

    # Cut off the unneeded bits in the LUT
    pwm_signal = mapped_intensity >> (16-self.bit_depth)
    #pwm_signal = mapped_intensity & (imax-1)

    return pwm_signal

  # Intensity between 0 and 255 (integer)
  def intensity_to_pwm(self, intensity):

    intensity = max(0, intensity)
    intensity = min(intensity, 255)

    n_steps = len(self.pwm)
    step = (intensity * n_steps) // 256

    #print(f"{intensity=} -> {step=} -> {self.pwm[step]=:#x}")
    return self.pwm[step]


  # Intensity is [0, 255]
  def set(self, x, y, intensity=255):
    #imax = 2**(self.bit_depth-1)

    #intensity = self.remap_intensity(intensity)
    pwm_bits = self.intensity_to_pwm(intensity)

    x = x % 16
    y = y % 16

    #intensity = min(intensity, ( imax ))

    # Index into our framebuffer (word-width)
    w = 0

    # Right half of frame
    if (x >=8): w+=4

    # Vertical position
    w += y//4

    b = (y%4)*8 + x%8


    for f in range(self.n_frames):
      word_addr = self.FRAME_BASE_ADDR + f*32 + w*4

      if pwm_bits >> f & 1 == 1:
        #self.fb[f][w] |= (1 << b)
        mem32[word_addr] |= (1 << b)
      else:
        #self.fb[f][w] &= (1 << b) ^ 0xFFFFFFFF
        mem32[word_addr] &= (1 << b) ^ 0xFFFFFFFF


  def autoflip(self):

    duration = self.intervals[self.flip_phase]

    freq = 1e4 // (duration)
    freq = int(freq * 1)

    self.frame_tim.init(freq=freq, mode=Timer.ONE_SHOT, callback=lambda t:self.autoflip())

    self.flip_phase = (self.flip_phase + 1) % self.bit_depth

    #self.set_frame(self.flip_phase)

  def start_auto_dma(self):
    freq = 1e1
    #self.dma_tim.init(freq=freq, mode=Timer.PERIODIC, callback=lambda t: micropython.schedule(self.dma_flip, (1,)))
    #self.dma_tim.init(freq=freq, mode=Timer.PERIODIC, callback=lambda t: self.dma_flip())

    # Kick start the trigger_dma, which will start the main_dma frame pump
    # Once main_dma finishes one set of frames, the trigger_dma will restart etc etc etc
    self.trigger_dma_chan.M0_CTRL_TRIG.EN = 1   # Go!


  
  def push(self, x):
    #self.matrix.set_matrix(array.array("I", self.fb[x]))
    #self.matrix.update()
    #self.set_frame(x)
    self.dma_flip()

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
    self.trigger_dma_chan.M0_READ_ADDR_REG = self.FRAME_BASE_PTR_ADDR

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



  def dma_flip(self, dc=None):
    while self.main_dma_chan.M3_CTRL.BUSY:
      time.sleep(0.001)


    # On alias mode 3, the write to READ_ADDR_REG is what triggers the DMA channel to start.
    self.main_dma_chan.M3_READ_ADDR_TRIG_REG = self.FRAME_BASE_ADDR