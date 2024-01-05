
import time
from machine import Pin

LONG_PRESS_MS=400
SHORT_PRESS_MS=4

# Returns (btn1, btn2)
# where 0 means no press,
# 1 means holding
# 2 means short press ended
# 3 means long press ended

BUTTONS = [ Pin(14, Pin.IN, Pin.PULL_UP), Pin(15, Pin.IN, Pin.PULL_UP) ]
BTN_PRESS_TIMES = [None, None]
def poll():
    # Our buttons are active low, so 0 means pressed

    ret = [0, 0]
    for b in range(len(BUTTONS)):
        state = BUTTONS[b].value()

        if not state:
            # Button down
            ret[b] = 1
            if BTN_PRESS_TIMES[b] is None:
                BTN_PRESS_TIMES[b] = time.ticks_ms()
            continue

        if BUTTONS[b].value():
            # Button up
            if BTN_PRESS_TIMES[b] is None:
                ret[b] = 0
                continue

            end_time = time.ticks_ms()
            diff_ms = time.ticks_diff(end_time, BTN_PRESS_TIMES[b])

            if diff_ms > LONG_PRESS_MS:
                ret[b] = 3
            elif diff_ms > SHORT_PRESS_MS:
                ret[b] = 2
            BTN_PRESS_TIMES[b] = None

    return tuple(ret)
