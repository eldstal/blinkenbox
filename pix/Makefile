all:
	for PY in *.py; do \
		[[ "$${PY}" != "main.py" ]] && mpremote fs cp "$${PY}" :$${PY}; \
	done
	mpremote fs cp video.fk :video.fk
	mpremote fs cp framebuddy.mpy :framebuddy.mpy

run:
	make all
	mpremote run video.py
