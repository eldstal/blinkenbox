#!/bin/env python3
# Test the menu in the comfort of your own terminal

# Terminal hacks stolen from stackoverflow, of course.

import sys
import termios
import tty
import select



from fakebuffer import FakeBuffer
import menu


my_tree = [
        {
            "result": "One",
            "icon": [ [255],
                      [255],
                      [255]
            ],

            # An entry with a sub menu
            "menu": [
                        {
                            "result": "Ey",
                            "icon": [[255, 0, ],
                                     [255, 0, ],
                                     [255, 0, 128]
                            ]
                        },

                        {
                            "result": "Bee",
                            "icon": [[255, 0, ],
                                     [255, 0, 128],
                                     [255, 0, 128]
                            ]
                        },

                        {
                            "result": "Cee",
                            "icon": [[255, 0, 128],
                                     [255, 0, 128],
                                     [255, 0, 128]
                            ]
                        }
            ]
        },
        {
            "result": "Two",
            "icon": [[255, 0, 255],
                     [255, 0, 255],
                     [255, 0, 255]
                    ]
            
        },
        {
            "result": "Three",
            "icon": [[255, 0, 255, 0, 255],
                     [255, 0, 255, 0, 255],
                     [255, 0, 255, 0, 255]
                    ]
            
        }

    ]


def input_waiting(blocking=True):

    while True:
        try:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                return True
        except:
            return False
        if not blocking: return False


def drive_menu(mnu, disp):

    while True:

        mnu.draw(disp)

        c = sys.stdin.read(1)
        
        keymap = {
            '\n':     menu.Action.OK,
            '\x7f':   menu.Action.BACK,
            'w':      menu.Action.UP,
            's':      menu.Action.DOWN,
            ' ':      menu.Action.TIMEOUT
        }

        if c not in keymap: continue

        exited, result = mnu.action(disp, keymap[c])

        # Menu terminated
        # result will be None if the user backed out
        if exited:
            return result



if __name__ == "__main__":

    disp = FakeBuffer()

    mnu = menu.Menu(my_tree)


    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        result = drive_menu(mnu, disp)
        print(result)


    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)