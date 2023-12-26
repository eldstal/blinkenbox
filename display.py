
class Display:
    def __init__(self):
        print("\033[2J")
        self.clear()

    def clear(self):
        self.px = []
        self.stack = []
        for y in range(16):
            self.px += [[0]*16]
            self.stack += [[0]*16]


    def push(self):
        for y in range(16):
            for x in range(16):
                self.stack[y][x] = self.px[y][x]
    
    def pop(self):
        for y in range(16):
            for x in range(16):
                self.px[y][x] = self.stack[y][x]

    def decay(self, amount):
        for y in range(16):
            for x in range(16):
                if self.px[y][x] > amount: self.px[y][x] -= amount
                else: self.px[y][x] = 0

    def glow(self):
        for y in range(16):
            for x in range(16):
                v = self.px[y][x]
                if v == 0: continue

                glow = v//64
                for dy in range(-1,2):
                    ny = (y + dy) % 16
                    for dx in range(-1,2):
                        nx = (x + dx) % 16
                        if self.px[ny][nx] != 0: continue

                        self.px[ny][nx] = glow

    def blur(self):
        bpx = []
        for y in range(16):
            bpx += [[0]*16]

        for y in range(16):
            for x in range(16):
                v = self.px[y][x]
                if v == 0: continue

                total = 0

                for dy in range(-1,2):
                    ny = (y + dy) % 16
                    for dx in range(-1,2):
                        nx = (x + dx) % 16
                        total += self.px[ny][nx]
                bpx[y][x] = total // 9
        self.px = bpx 


    def ascii(self, px):
        if px == 0: return " "
        if px < 64: return ":"
        if px < 128: return "+"
        if px < 192: return "*"
        return "#"

    def update(self):
        print("\033[17A")
        for row in self.px:
            text = "".join([self.ascii(px) for px in row])

            print(text,)

