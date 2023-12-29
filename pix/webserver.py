import network
import socket
from time import sleep
import machine
import socket
import fb

SSID = "37C3-open"
PASSWORD = None

def err404(msg):
    #Template HTML
    html = f"""<!DOCTYPE html>
            <html>
            <h1>404</h1>
            <span>{msg}</span>
            </html>
            """
    return str(html)

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
        self.handler = {
            "GET" : {},
            "POST" : {}
        }

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

    def serve(self, frame):
        self.open_socket()
        while True:
            client = self.s.accept()[0]
            request = client.recv(2048)
            #request = str(request)[2:-1]
            #print(request)
            try:
                rs = request.split()
                path = rs[1].decode()
                verb = rs[0].decode()
            except IndexError:
                client.send(err404("path or verb missing"))
                return
            
            try:
                client.send( self.handler[verb.upper()][path.upper()].handle(request))
            except KeyError:
                client.send(err404(f"{verb.upper()} {path.upper()} failed"))
            client.close()
    
    def register(self, handler):
        self.handler[handler.verb.upper()][handler.path.upper()] = handler

class handle_index:
    def __init__(self):
        self.path = "/"
        self.verb = "GET"
    
    def handle(self, request):
        html = f"""<!DOCTYPE html>
                <html>
                hello
                </html>
                """
        return str(html)

def hexdump(s):
    ret = ""
    i = 0
    for x in s:
        if i == 8:
            i = 0
            ret += "\n"
        ret += f"{ord(x):02x} "
        i+=1
    return ret

import json
class handle_frame:
    def __init__(self, fb):
        self.path = "/frame"
        self.verb = "POST"
        self.fb = fb
    # Fix me dosent work since we dont get all data.
    def handle(self, request):
        print(hexdump(request))
        try:
            frame = json.loads(request.split("\r\n\r\n")[1])
        except IndexError:
            return ""
        
        self.fb.clear()
        for y,row in frame.items():
            for x, val in enumerate(row):
                self.fb.set(x,int(y),val)
                print(f"y{y} x{x} val{val}")
        
        self.fb.flip()
        return "HTTP/1.1 200 ok\r\n"
import struct
class handle_binframe:
    def __init__(self, fb):
        self.path = "/binframe"
        self.verb = "POST"
        self.fb = fb
    
    def handle(self, request):
        #print(hexdump(request))
        try:
            #frame = bytearray()
            frame = request.split(b"\r\n\r\n")[1]
        except IndexError:
            return ""
        
        self.fb.clear()
        extra = None
        for y,row in enumerate(struct.unpack("h"*16, frame)):
            for x in range(16):
                self.fb.set(x, y, (row>>(15-x))&1)
                print(f"x{x}, y{y}, val{(row>>(15-x))&1}")
        
        self.fb.flip()
        return "HTTP/1.1 200 ok\r\n"

if __name__ == "__main__":
    try:
        frame = fb.Framebuf()
        w = webserver(SSID, frame)
        w.register(handle_index())
        w.register(handle_frame(frame))
        w.register(handle_binframe(frame))
        w.connect()
        print(w.ip)
        w.serve(frame)
    except KeyboardInterrupt:
        machine.reset()