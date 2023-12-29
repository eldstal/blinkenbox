"""
Compress files using basic run-length-encoding.

Works both on micropython and on big boy python.
If called as a tool, can be used to compress and decompress
RLE files.
"""


def deflate_rle(data):
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


def inflate_rle(data):
    b = 0
    for i, byte in enumerate(data):
        if i % 2 == 0:
            b = byte
        else:
            for _ in range(byte):
                yield b


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", type=argparse.FileType("rb"), nargs="*", default=[sys.stdin]
    )
    parser.add_argument(
        "-o", "--output", type=argparse.FileType("wb", 0), nargs="?", default="-"
    )
    parser.add_argument("-x", "--extract", action="store_true")
    args = parser.parse_args()

    if args.extract:
        if len(args.input) > 1:
            sys.exit("Can only extract single image")
        args.output.write(bytes(inflate_rle(args.input[0].read())))
    else:
        for image in args.input:
            args.output.write(bytes(deflate_rle(image.read())))
