import struct
import socket
import time
import sys

if __name__ == "__main__":
    for i in range(1000):
        sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
        sock.connect((sys.argv[1], int(sys.argv[2])))
        
        frame = bytearray()
        for y in range(16):
            data = 0
            for x in range(16):
                data = (data << 1) + ((y+x+i)%2)
            frame.append(data&0xff)
            frame.append((data>>8)&0xff)
        print({len(frame)})
        frame = struct.pack("HH", 1, len(frame)) + frame
        print(frame)
        time.sleep(1)
        sock.send(frame)
        sock.close()
