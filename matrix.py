from machine import Pin, mem32, PWM
from time import sleep
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


def clamp(n, minimum=0, maximum=1):
    return min(maximum, max(minimum, n))


class matrix:
    def __init__(self, brightness=0.55):
        self.level = clamp(brightness)
        self.freq = 500
        SM0_EXECCTRL = 0x0CC
        mem32[SM0_EXECCTRL] |= 0x0000001F  # set up status == FIFO_FULL

        self.sm = rp2.StateMachine(
            0, matrix_pio, freq=2_000_000, out_base=Pin(DATA), sideset_base=Pin(LATCH)
        )
        self.sm.active(1)

        self.matrix = array.array("I", [0xFFFFFFFF] * 8)

        self.dimmer = PWM(ENABLE, freq=self.freq, duty_u16=0)
        self.dim()

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
    m = matrix()

    print("send")
    m.update()
    m.clear()
    sleep(1)
    m.update()
    sleep(1)
    m.set_matrix(array.array("I", [0xaaaaaaaa]*16))
    m.update()
    sleep(1)
    m.set_matrix(array.array("I", [0x55555555]*16))
    m.update()
    print("done")
