from machine import Pin, mem32
from time import sleep
import rp2
import array

@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,),
    sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
    fifo_join=rp2.PIO.JOIN_TX,
    autopull=True
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
ENABLE = Pin(Pin.board.GP3, Pin.OUT)

class matrix:
    def __init__(self):
        SM0_EXECCTRL = 0x0cc
        mem32[SM0_EXECCTRL] |= 0x0000001F # set up status == FIFO_FULL

        self.sm = rp2.StateMachine(0, matrix_pio, freq=20_000_000, out_base=Pin(DATA), sideset_base=Pin(LATCH))
        self.sm.active(1)
        ENABLE.off()

        self.matrix = array.array("I", [0xffffffff]*16)

    def push_frame(self):
        self.sm.put(self.matrix)
    
    def set_matrix(self, arr):
        self.matrix = arr
    
    def clear(self):
        self.set_matrix(array.array("I", [0x0]*16))
#@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW))
#def full_send():
#    pull()
#    out(pins, 4) [31]

if __name__ == "__main__":
    m = matrix()

    print("send")
    m.push_frame()
    m.clear()
    sleep(1)
    m.push_frame()
    sleep(1)
    m.set_matrix(array.array("I", [0xaaaaaaaa]*16))
    m.push_frame()
    sleep(1)
    m.set_matrix(array.array("I", [0x55555555]*16))
    m.push_frame()
    print("done")
