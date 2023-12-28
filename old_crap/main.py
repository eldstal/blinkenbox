
import board
import digitalio


from display import Display
import snake
import twinkle
import sink

LED = digitalio.DigitalInOut(board.LED)
LED.direction=digitalio.Direction.OUTPUT

DISP = Display()

# Indicate on the on-board LED
def flash(on,off):
    LED.value = True
    time.sleep(on)
    LED.value = False
    time.sleep(off)

#snake.main(DISP)
#twinkle.main(DISP)
sink.main(DISP)