import network
import socket
from time import sleep
import machine
import socket
import fb

SSID = "37C3-open"
PASSWORD = None

errtable = {
    2:"unknown",
    network.STAT_IDLE : "IDLE",
    network.STAT_CONNECTING : "CONNECTING",
    network.STAT_WRONG_PASSWORD : "WRONG PASSWORD",
    network.STAT_NO_AP_FOUND : "AP NOT FOUND",
    network.STAT_CONNECT_FAIL : "CONNECT FAIL",
    network.STAT_GOT_IP : "GOT IP"
}

class webserver:
    def __init__(self, ssid, framebuf, password=None):
        self.framebuf = framebuf
        self.ip = None
        self.netmask = None 
        self.gateway = None
        self.dns = None
        self.wlan = None
        self.ssid = ssid
        self.password = password
        self.handler = {}

    def connect(self):
        ap_if = network.WLAN(network.AP_IF)
        if ap_if.active():
            ap_if.active(False)

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True) 
        self.wlan.connect(SSID,None)
        while not self.wlan.isconnected():
            print(f"trying to join wifi {SSID}, status {errtable[self.wlan.status()]}")
            if self.wlan.status() == network.STAT_CONNECT_FAIL:
                self.wlan.connect(SSID,None)
            if self.wlan.status() == network.STAT_NO_AP_FOUND:
                self.wlan.connect(SSID,None)
            sleep(1)
        self.ip, self.netmask, self.gateway, self.dns = self.wlan.ifconfig()

    def scanssids(self):
        if self.wlan:
            return [ x[0] for x in self.wlan.scan()]
        return None

    def open_socket(self):
        addr = (self.ip,80)
        self.s = socket.socket()
        self.s.bind(addr)
        self.s.listen(1)

    def serve(self):
        self.open_socket()
        while True:
            client = self.s.accept()[0]
            data = client.recv(2048)
            cmd, size = struct.unpack("HH", data[:4])
            print(f"cmd:{cmd}, size{size}, len(data[4:]){len(data[4:])}")
            while len(data[4:]) < size:
                data += client.recv(2048)
                print(f"cmd:{cmd}, size{size}, len(data[4:]){len(data[4:])}")
            try:
                self.handler[cmd].handle(data[4:])
            except KeyError:
                print(f"no handler for cmd{cmd}")
            client.close()
    
    def register(self, handler):
        self.handler[handler.command] = handler

def hexdump(s):
    ret = ""
    i = 0
    for x in s:
        if i == 8:
            i = 0
            ret += "\n"
        if type(x) == str:
            ret += f"{ord(x):02x} "
        else:
            ret += f"{x:02x} "
        i+=1
    return ret

import struct
class handle_binframe:
    def __init__(self, fb):
        self.command = 1
        self.size = 32
        self.fb = fb

    def handle(self, data):
        if len(data) != self.size:
            print(f"expeted size {self.size} got {len(data)}")
        self.fb.clear()
        for y,row in enumerate(struct.unpack("h"*16, data)):
            for x in range(16):
                self.fb.set(x, y, (row>>(15-x))&1)
                print(f"x{x}, y{y}, val{(row>>(15-x))&1}")
        
        self.fb.flip()
        return 

if __name__ == "__main__":
    try:
        frame = fb.Framebuf()
        w = webserver(SSID, frame)
        w.register(handle_binframe(frame))
        w.connect()
        print(w.ip)
        w.serve()
    except KeyboardInterrupt:
        machine.reset()