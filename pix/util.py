def bitwise(data):
    """split a bytes iterable into a bits iterable. a bitserable."""
    for byte in data:
        for bit in range(8):
            yield byte >> bit & 1

def fullbright(data):
    """for each value in data, return 1 if it is not 0."""
    for b in data:
        yield int(b > 0)

def auto_rewind(filename):
    """read through file repeatedly"""
    with open(filename, "rb") as f:
        run = True
        while run:
            f.seek(0)
            b = f.read(1)
            while b:
                run = (yield b[0]) is None
                b = f.read(1)
            
            
def clamp(n, low=0, high=1):
    """this is a clamp(). it clamp()s."""
    return max(low, min(n, high))

def lerp(src, dst, progress):
    """man vet aldrig när man kan behöva en schysst lerp"""
    return src + progress * (dst - src)
