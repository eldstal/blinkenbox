import matrix
import array
import uctypes

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
    self.fb = []
    for i in range(8):
      self.fb.append(bytearray(32+24))

    self.FRAME_ADDR = array.array("L", [ uctypes.addressof(self.fb[f]) for f in range(8) ])

    self.matrix = matrix.matrix(brightness=0.50)
    #self.start()

    self.flip_phase = 0

    self.bit_depth = 4

    self.dma_setup()

    self.set_frame(0)


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

    # Push frames to PIO periodically
    #self.start_auto_dma()

    # Swap framebuffer at set intervals
    #self.autoflip()

  def clear(self):
    for f in range(8):
      for w in range(8):
        #self.fb[f][w] = 0
        word_addr = self.FRAME_ADDR[f] + w*4
        mem32[word_addr] = 0

  def set_frame(self, f):
    self.CURRENT_FRAME_ADDR = self.FRAME_ADDR[f]

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


  def set(self, x, y, intensity=15):
    imax = 2**(self.bit_depth-1)

    #intensity = self.remap_intensity(intensity)

    x = x % 16
    y = y % 16

    intensity = min(intensity, ( imax ))

    # Index into wpx (word)
    w = 0

    # Right half of frame
    if (x >=8): w+=4

    # Vertical position
    w += y//4

    b = (y%4)*8 + x%8


    for f in range(8):
      word_addr = self.FRAME_ADDR[f] + w*4

      if intensity >> f & 1 == 1:
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

    self.set_frame(self.flip_phase)

  def start_auto_dma(self):
    freq = 1e1
    self.dma_tim.init(freq=freq, mode=Timer.PERIODIC, callback=lambda t:self.dma_flip())


  
  def push(self, x):
    #self.matrix.set_matrix(array.array("I", self.fb[x]))
    #self.matrix.update()
    self.set_frame(x)
    self.dma_flip()

  def dma_setup(self):

    self.dma_chan = devs.DMA_CHANS[0]
    self.dma = devs.DMA_DEVICE

    self.dma_chan.WRITE_ADDR_REG = devs.PIO0_TX

    # One frame per transfer
    self.dma_chan.TRANS_COUNT_REG = 8

  def dma_flip(self):
    while self.dma_chan.CTRL_TRIG.BUSY:
      time.sleep(0.001)

    self.dma_chan.READ_ADDR_REG = self.CURRENT_FRAME_ADDR

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

    self.dma_chan.CTRL_TRIG_REG=0
    self.dma_chan.CTRL_TRIG.DATA_SIZE=2    # One 32b word at a time
    self.dma_chan.CTRL_TRIG.INCR_READ = 1  # Eat the READ buffer
    self.dma_chan.CTRL_TRIG.INCR_WRITE = 0 # Only one target word
    self.dma_chan.CTRL_TRIG.RING_SEL = 0   # Wrap the READ buf
    self.dma_chan.CTRL_TRIG.RING_SIZE = 5  # Wrap on 32 bytes (1 frame)

    self.dma_chan.CTRL_TRIG.IRQ_QUIET = 1
    self.dma_chan.CTRL_TRIG.TREQ_SEL = devs.DREQ_PIO0_TX0 # Send only when the PIO is ready to receive

    self.dma_chan.CTRL_TRIG.EN = 1   # Go go go go go

