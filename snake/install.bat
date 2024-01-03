mpremote fs cp ..\matrix.py :matrix.py
mpremote fs cp ..\fb.py :fb.py
mpremote fs cp ..\util.py :util.py
mpremote fs cp ..\file.py :file.py
mpremote fs cp ..\rp_devices.py :rp_devices.py
mpremote fs cp ..\framebuddy.mpy :framebuddy.mpy

mpremote fs cp snake.py :snake.py

mpremote reset
timeout /t 2
mpremote run go.py
