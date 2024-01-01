
def fullbright(data, threshold=0):
    """treat 8bpp data as 1bpp."""
    for b in data:
        yield int(b > threshold)


            
def clamp(n, low=0, high=1):
    """this is a clamp(). it clamp()s."""
    return max(low, min(n, high))

def lerp(src, dst, progress):
    """man vet aldrig när man kan behöva en schysst lerp"""
    return src + progress * (dst - src)
