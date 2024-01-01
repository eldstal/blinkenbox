from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import struct
import socket
import config

app = FastAPI()

def buildPackage(cmd, data):
    return struct.pack("HH", cmd, len(data)) + data

def sendFrame(frame):
    print()
    binframe = bytearray()
    for y, row in frame.items():
        binrow = 0
        for x, value in row.items():
            binrow = (binrow<<1) |value
            print(value, end=" ")
        binframe.append(binrow&0xff)
        binframe.append((binrow>>8)&0xff)
        print()
    print(binframe)
    print()

    sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)
    sock.connect((config.ip, config.port))
    sock.send(buildPackage(1,binframe))
    sock.close()

@app.get("/")
async def get():
    html = ""
    with open("index.html", "r") as f:
        html = f.read()
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        sendFrame(json.loads(data))