#
# CircuitPython
#


import os
import sys
import time
import select
import wifi
import board
import digitalio

import netz
import socketpool


class Sink:
    def __init__(self, maxage=25):
        pass
    
    def start(self):
        pass


    def tick(self, disp, sock):
        disp.decay(5)

        ready,_,_ = select.select([sock], [], [], 0.3)

        if len(ready) > 0:
            
            buf = bytearray(16*16)
            for r in ready:
                n_bytes, src = r.recvfrom_into(buf)

            for y in range(16):
                for x in range(16):
                    idx = y*16 + x
                    val = buf[idx]
                    disp.px[y][x] = max(disp.px[y][x], val)

        disp.update()
    
    def main(self, disp):
        local_addr, mask, gw, dns = netz.ifconfig()

        pool = socketpool.SocketPool(wifi.radio)

        img_sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
        img_sock.bind((str(local_addr), 1337))

        ticker = lambda: self.tick(disp, img_sock)

        netz.loop_with_net(ticker)
            


networks = [
              {
                "ssid": os.getenv("CIRCUITPY_WIFI_SSID"),
                "psk": os.getenv("CIRCUITPY_WIFI_PASSWORD")
              }
           ]

def main(display):

    

    while True:
        netz.try_connect(networks)

        DEMO = Sink()
        DEMO.start()
        DEMO.main(display)


