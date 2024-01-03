## Blinkenbox

Some fancy drivers and demos for an IKEA Frekvens LED box, powered by a Raspberry Pi Pico-W

### What's so great about this?!
The LED matrix of FREKVENS is based on single-bit shift registers. That means you shift a
serial bit stream of 256 pixel states into it and then LATCH to show the values in the LED
array.

That hardware doesn't support dimming of individual pixels.

This repo implements Binary Code Modulation, as described by SpritesMods [here](https://spritesmods.com/?art=frekvens&page=4) and Batsocks [here](http://www.batsocks.co.uk/readme/art_bcm_3.htm).

The actual driving of the display is done *entirely without* CPU intervention. There are no timers, interrupts or bit-banging involved. In fact, Blinkenbox doesn't even use any of the transceivers on the RP2040 chip!

As a joke, a punishment and a cool trick, the LED driver is implemented entirely in Programmable I/O (see `matrix.py`) and driven by multiple autonomous DMA channels (see `fb.py`). Using these methods, the pico-w is able to display about 2000 raw single-bit images per second. When BCM is added to perform brightness modulation over 32 frames, the system can draw about 62FPS with a 5-bit grayscale depth. This comes at no cost in terms of CPU utilization, since all data shuffling is performed by DMA controllers and Programmable I/O.

## Pinout

```
GP0: LATCH (gray)
GP1: CLK (yellow)
GP2: DATA (blue)
GP3: ENABLE (green)
GP13: Button COM (red)
GP14: Button 1 (white)
GP15: Button 2 (Black)
```


![Cable colors on motherboard](doc/box_cabling.jpg)
![Cable colors on Raspi Pico](doc/pico_cabling.jpg)
![Cable colors on Raspi Pico](doc/cable_mapping.jpg)


## Interference
Separate the red VSYS cable from the signal wires!! Otherwise you'll likely get strange artefacts when the USB is connected

![Don't mix signals and power](doc/separation.jpg)
