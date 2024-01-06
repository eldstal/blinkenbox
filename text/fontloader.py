

class Font:

    def __init__(self, fontpath):

        self.width = 0
        self.height = 0
        self.spacing = 1

        self.charmap = {}

        self.parse(open(fontpath, "rb"))

    def parse(self, fontfile):
        header = fontfile.read(1)[0]
        bytes_per_char = (header >> 4) & 0xF
        bits_per_row = (header) & 0xF

        self.width = bits_per_row
        self.height = (bytes_per_char * 8) // bits_per_row

        print(f"Parsing font for {self.width}x{self.height} characters")

        # These characters come first, in this order
        charcodes = list(range(ord('A'), ord('Z')+1)) + list(range(ord('0'), ord('9')+1))

        for c in charcodes:
            bits = fontfile.read(bytes_per_char)
            if len(bits) != bytes_per_char:
                print("Font file ended early. Font incomplete.")
                break

            bitmask = int.from_bytes(bits, "big")
            self.charmap[c] = bitmask
        
        print(f"Loaded {len(self.charmap)} basic characters")

        newline = fontfile.read(1)

        # Special chars come next, prefixed by their ASCII encoding
        while True:
            try:
                c = fontfile.read(1)[0]
            except:
                break

            bits = fontfile.read(bytes_per_char)
            if len(bits) != bytes_per_char:
                print(f"Font file ended early (special char {c:#02x}). Font incomplete.")
                break

            bitmask = int.from_bytes(bits, "big")
            self.charmap[c] = bitmask
        
        print(f"Loaded {len(self.charmap)} characters in total")


    # Returns a generator of (x,y) pairs to light up
    def charpixels(self, bitmask):

        # TODO: Optimize calculation of x and y. Shouldn't need a branch.
        x = self.width-1
        y = self.height-1

        ret = []

        for b in range(self.width*self.height):
            bit = bitmask & 0x1
            bitmask = bitmask >> 1

            if bit:
                yield (x,y)
            
            x -= 1
            if (x < 0):
                y -= 1
                x = self.width-1

        return ret


    # Directly places text on the framebuffer
    # Does not wrap text
    def draw(self, disp, x, y, text, brightness=128):

        for char in text:
            c = ord(char)
            if c in self.charmap:
                for cx,cy in self.charpixels(self.charmap[c]):
                    disp.set(x+cx, y+cy, brightness)
            x += self.width + self.spacing
