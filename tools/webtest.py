import requests
import json
from collections import defaultdict
import base64
import sys

if __name__ == "__main__":
    """requests.packages.urllib3.connection.HTTPConnection.default_socket_options = [(6,3,1)]
    d = defaultdict(list)
    for y in range(16):
        d = defaultdict(list)
        for x in range(16):
            d[y].append((y+x)%2)

        x = requests.post("http://151.217.109.32/frame", data = json.dumps(d))
        print(x.text)
    """
    requests.packages.urllib3.connection.HTTPConnection.default_socket_options = [(6,3,1)]
    
    for i in range(1000):
        frame = bytearray()
        for y in range(16):
            data = 0
            for x in range(16):
                data = (data << 1) + ((y+x+i)%2)
            frame.append(data&0xff)
            frame.append((data>>8)&0xff)
        print(frame)
        x = requests.post(f"http://{sys.argv[1]}/binframe", data = frame, headers={'Content-Type': 'application/octet-stream'})