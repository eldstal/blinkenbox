import sys

with open(sys.argv[1], "rb") as f:
    data = f.read()


with open(sys.argv[1], "wb") as f:
    f.write(data[::3])
