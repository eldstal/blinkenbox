"""
File utilities for frekvensfiles (.fk)

Works both on micropython and on big boy python.
If called as a tool, can be used to encode and decode frekvensfiles.
"""

from util import fullbright

MAGIC = 0xF8


def fkencode(data, bpp=8, compress=True, animated=False):
    if bpp == 1:
        if compress:
            raise ValueError("RLE compression as implemented is useless at 1bpp")
        body = encode_1bpp(data)
    elif bpp == 8:
        if compress:
            body = compress_rle(data)
        else:
            body = data
    else:
        raise NotImplementedError("Only supports 1 and 8 bpp")

    header = MAGIC
    header |= int(bpp == 8)
    header |= int(compress) << 1
    header |= int(animated) << 2

    yield header
    yield from body


def fkopen(filename, **options):
    """Open a frekvensfile as a stream"""
    with open(filename, "rb") as f:
        yield from fkdecode(stream(f), **options)


def fkdecode(data, bytewise=None, compressed=None, animated=None, brightness_hack=False):
    """read frekvensfile header and configure output stream"""

    head = next(data)
    if (head & MAGIC) != MAGIC:
        raise ValueError(f"bad magic {head:2x}")

    bytewise = bool(head & 1) if bytewise is None else bytewise
    compressed = bool(head & 2) if compressed is None else compressed
    animated = bool(head & 4) if animated is None else animated
    print(f"{bytewise=}, {compressed=}, {animated=}")

    data.send({"offset": 1, "rewind": animated})
    if compressed:
        data = extract_rle(data)
    if bytewise:  # TODO: fix for brighthack
        if not brightness_hack:
            data = fullbright(data)
    else:
        data = decode_1bpp(data)
    yield from data


def stream(fd, offset=0, rewind=False):
    """Stream a file byte by byte"""
    while True:
        fd.seek(offset)
        b = fd.read(1)
        while b:
            options = yield b[0]
            if options is not None:
                fd.seek(-1, 1)  # send wastes a value :( 
                offset = options.get("offset", offset)
                rewind = options.get("rewind", rewind)

            b = fd.read(1)
        if not rewind:
            break


def encode_1bpp(data):
    """Given a 8bpp 1-channel grayscale image, compress it to 1bpp"""

    byte = 0
    for i, b in enumerate(fullbright(data)):
        print(b, end="")
        byte |= b << (7 - (i % 8))
        if i > 0 and i % 8 == 7:
            yield byte
            byte = 0

def decode_1bpp(data):
    """split a bytes iterable into a bits iterable. a bitserable."""
    for byte in data:
        for bit in range(8):
            yield byte >> (7 - bit) & 1


def compress_rle(data):
    """Run-length-encode a byte stream as pairs of (value, count)"""
    prev = None
    count = 0
    for i, b in enumerate(data):
        if b != prev or count == 255:
            if prev is not None:
                yield prev
                yield count
            prev = b
            count = 0
        count += 1
    yield prev
    yield count


def extract_rle(data):
    """unpack a run-length-encoded byte stream"""
    value = 0
    for i, byte in enumerate(data):
        if i % 2 == 0:
            value = byte
            continue
        for _ in range(byte):
            yield value


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    cmd = parser.add_subparsers(required=True)

    enc = cmd.add_parser("encode")
    enc.set_defaults(command="encode")
    enc.add_argument(
        "input", type=argparse.FileType("rb"), nargs="*", default=[sys.stdin]
    )
    enc.add_argument(
        "-o", "--output", type=argparse.FileType("wb", 0), nargs="?", default="-"
    )
    enc.add_argument("-1", "--one-bpp", action="store_true")
    enc.add_argument("-c", "--compress", action="store_true")
    enc.add_argument("-a", "--animated", action="store_true")

    dec = cmd.add_parser("decode")
    dec.set_defaults(command="decode")
    dec.add_argument(
        "input", type=argparse.FileType("rb"), nargs="?", default=[sys.stdin]
    )
    dec.add_argument(
        "-o", "--output", type=argparse.FileType("wb", 0), nargs="?", default="-"
    )
    args = parser.parse_args()

    try:
        if args.command == "decode":
            out = fkdecode(stream(args.input), animated=False, bytewise=False)
            args.output.write(out)
        else:
            animated = args.animated or len(args.input) > 1
            bpp = 1 if args.one_bpp else 8
            for image in args.input:
                out = fkencode(stream(image), bpp, args.compress, animated)
                args.output.write(bytes(out))
    except ValueError as err:
        sys.exit(err)
