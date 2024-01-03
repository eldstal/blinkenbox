all:
	for PY in *.py; do \
		[ "$${PY}" != "main.py" ] && mpremote fs cp "$${PY}" :$${PY}; \
	done
	for DEP in ../*.py; do \
		mpremote fs cp "$${DEP}" :`basename $${DEP}`; \
	done

run:
	make all
	mpremote run go.py
