mpremote fs cp ..\matrix.py :matrix.py
mpremote fs cp ..\fb.py :fb.py
mpremote fs cp ..\rp_devices.py :rp_devices.py
mpremote fs cp ..\framebuddy.mpy :framebuddy.mpy

mpremote fs cp ..\text\font.py :font.py
mpremote fs cp ..\text\fonts\3x5.fnt :3x5.fnt

mpremote fs cp menu.py :menu.py
mpremote fs cp buttons.py :buttons.py
mpremote fs cp demo_snake.py :demo_snake.py
mpremote fs cp demo_matrix.py :demo_matrix.py
mpremote reset
timeout /t 2
mpremote run go.py

