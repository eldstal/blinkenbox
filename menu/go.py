#
# A demo of the menu, using demos
#


import buttons
import menu
import fb

import demo_snake
import demo_matrix



if __name__ == "__main__":

    disp = fb.Framebuf()

    mnu = menu.Menu( [         
        {
            "result": "demo",
            "icon": [
                [ 180, 180, 32],
                [ 180, 0,   180 ],
                [ 180, 0,   180],
                [ 180, 0,   180],
                [ 180, 180, 32],
            ],
            "menu": [
                {
                    "result": "snake",
                    "icon": [
                        [255,   0,    255,   96,  255 ],
                        [96,    0,    96,    0,   96 ],
                        [255,   0,    255,   0,   32 ],
                        [96,    0,    96,    0,   16 ],
                        [255,   96,   255,   0,   0 ],
                    ]

                },

                {
                    "result": "matrix",
                    "icon": [
                        [90,    20,    35,   120,  255 ],
                        [90,    20,    35,   120,   0 ],
                        [90,    20,    255,  120,   0 ],
                        [90,    255,   0,    120,   0 ],
                        [255,   0,     0,    255,   0 ],
                    ]

                }

            ]
        },

        # Just a dummy entry to demonstrate the menus
        # This could of course have its own sub-menu, as needed
        {
            "result": "settings",
            "icon": [
                [ 180, 180, 32],
                [ 180, 0,   0 ],
                [ 32,  180, 32],
                [ 0,   0,   180],
                [ 32, 180,  180],
            ],

        }

    ])

    
    in_menu = True
    current_demo = "matrix"

    while True:
        a, b = buttons.poll()
        #if a>0 or b > 0: print(f"{in_menu=} {a=} {b=}")

        if in_menu:

            done = False
            result = None

            mnu.draw(disp)

            if a == 2:  # Short red
                done,result = mnu.action(disp, menu.Action.OK)
            
            if a == 3:  # Long red
                done, result = mnu.action(disp, menu.Action.BACK)

            if b > 1:  # Any yellow press
                done, result = mnu.action(disp, menu.Action.DOWN)

            if done:
                in_menu = False
                if result:
                    if result[0] == "demo":
                        current_demo = result[1]
                        print(f"Starting {current_demo}")

        else:
            if b > 1:   # Any yellow press
                in_menu = True
                continue

            if current_demo == "snake":
                demo_snake.tick(disp)

            if current_demo == "matrix":
                demo_matrix.tick(disp)