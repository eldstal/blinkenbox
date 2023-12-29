from machine import Pin, mem32, PWM
from time import sleep
from util import clamp
import rp2
import array

# fmt: off
@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,),
    sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
    fifo_join=rp2.PIO.JOIN_TX,
    out_shiftdir=rp2.PIO.SHIFT_RIGHT,
    autopull=True,
)
def matrix_pio():
    label("wait_full")
    set(x, status)              .side(0b00)
    jmp(not_x, "wait_full")     .side(0b00)
    set(y, 7)                   .side(0b00)
    label("next_word")
    set(x, 31)                  .side(0b00)
    label("bit_loop")
    out(pins, 1)                .side(0b00) [2]
    jmp(x_dec, "bit_loop")      .side(0b10) [2]
    jmp(y_dec, "next_word")     .side(0b00)
    nop()                       .side(0b01)

LATCH = Pin.board.GP0
CLK = Pin.board.GP1
DATA = Pin.board.GP2
ENABLE = Pin.board.GP3


class matrix:
    def __init__(self, brightness=0.55):
        self.level = clamp(brightness)
        self.freq = 80000
        SM0_EXECCTRL = 0x0CC
        mem32[SM0_EXECCTRL] |= 0x0000001F  # set up status == FIFO_FULL
        Pin(ENABLE, Pin.OUT).off()
        self.sm = rp2.StateMachine(
            0, matrix_pio, freq=25_000_000, out_base=Pin(DATA), sideset_base=Pin(LATCH)
        )
        self.sm.active(1)
        
        #self.matrix = array.array("I", [0xFFFFFFFF] * 8)

        #self.dimmer = PWM(ENABLE, freq=self.freq, duty_u16=0)
        #self.dim()
        #self.update()

    def update(self):
        self.sm.put(self.matrix)

    def set_matrix(self, arr):
        self.matrix = arr

    def clear(self):
        self.set_matrix(array.array("I", [0x0] * 8))

    def dim(self, level=None):
        self.level = clamp(level or self.level)

        print(f"Testing intensity {self.level}")

        duty = int((1 - self.level) * 65536)
        self.dimmer.duty_u16(duty)


if __name__ == "__main__":
    m = matrix(brightness=0)

    print("send")
    m.clear()
    m.update()

    fade_fraction = 1 / 32
    fade = 0

    display = array.array("I", [0xFFFF0000] * 8)
    flip = array.array("I", [0x0000FFFF] * 8)

    while True:
        if fade > 1 or fade < 0:
            fade_fraction = -fade_fraction
        if fade < 0:
            display, flip = flip, display
        fade += fade_fraction
        m.dim(fade)
        m.set_matrix(array.array("I", display))
        m.update()
        sleep(0.05)
    print("done")
    m.clear()
    m.update()
    sleep(1)
