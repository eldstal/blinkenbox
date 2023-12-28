from machine import Pin, mem32
from time import sleep
import rp2

@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_LOW,),
    sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
    fifo_join=rp2.PIO.JOIN_TX,
    autopull=True
)
def matrix():
    label("wait_full")
    set(x, status)              .side(0b00)
    jmp(not_x, "wait_full")     .side(0b00)
    set(y, 7)                   .side(0b00)
    label("next_word")
    set(x, 31)                  .side(0b00)
    label("bit_loop")
    out(pins, 1)                .side(0b00)
    jmp(x_dec, "bit_loop")      .side(0b10)
    jmp(y_dec, "next_word")     .side(0b00)
    nop()                       .side(0b01)

#@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW))
#def full_send():
#    pull()
#    out(pins, 4) [31]


LATCH = Pin.board.GP0
CLK = Pin.board.GP1
DATA = Pin.board.GP2
ENABLE = Pin(Pin.board.GP3, Pin.OUT)

SM0_EXECCTRL = 0x0cc

mem32[SM0_EXECCTRL] |= 0x0000001F

ENABLE.off()



print("start")
sm = rp2.StateMachine(0, matrix, freq=2000, out_base=Pin(DATA), sideset_base=Pin(LATCH))
print(sm.active(1))

print("send")
for i in range(16):
    sm.put(0xFFFFFFFF)
sleep(1)
for i in range(16):
    sm.put(0x00000000)


print("done")
                