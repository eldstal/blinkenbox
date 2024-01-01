all:
	for PY in *.py; do \
		[[ "$${PY}" != "main.py" ]] && mpremote fs cp "$${PY}" :$${PY}; \
	done
	mpremote fs cp video.fk :video.fk

run:
	make all
	mpremote run video.py
