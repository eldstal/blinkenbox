fnt file

## Header
1 byte

0010 0011
1st nibble: bytes per char
second nibble: bits per row (padding bits at the beginning of each character are ignored)

## Body

characters, in order:
```
ABCDEFGHIJKLMNOPQRSTUVXYZ0123456789
```

Next, a newline followed by any special characters.
Each character is the ASCII followed by its font bits



## Example

The following hexdump represents a 3x5 font with two special characters, `.` (ASCII 2E) and `,` (ASCII 2C).
```
232bed6bae39236b6e79e779e4392b5bed2492126a5bad49275eed5ffd7b6f7be47b7b6bad388e74925b6f5b6a5b7d5aad5b5272a77bef2c972a57638e17c9798e15aa72a42aaa2ad40a2e00022c0014
```


## Hex format
For creating the fonts, use the .fnt.hex format, which is all hex encoded and ignores whitespace

See 3x5.fnt.hex for an example, and use the `fnt2hex` script to "compile" into a binary .fnt file.
