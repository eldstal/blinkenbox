all:
	for PY in *.py; do \
		mpremote fs cp "$${PY}" :$${PY}; \
	done

run:
	make all
	mpremote run main.py
