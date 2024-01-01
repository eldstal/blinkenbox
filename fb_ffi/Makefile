all:
	for PY in *.py; do \
		[[ "$${PY}" != "main.py" ]] && mpremote fs cp "$${PY}" :$${PY}; \
	done

run:
	make all
	mpremote run go.py
