mpremote fs cp ..\matrix.py :matrix.py
mpremote fs cp ..\fb.py :fb.py
mpremote fs cp ..\rp_devices.py :rp_devices.py
mpremote fs cp ..\framebuddy.mpy :framebuddy.mpy

mpremote fs cp fontloader.py :fontloader.py
mpremote fs cp fonts\3x5.fnt :3x5.fnt

mpremote reset
timeout /t 2
mpremote run go.py
