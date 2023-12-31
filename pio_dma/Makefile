#ADDITIONAL_SOURCES=$(filter-out go.py,$(wildcard %.py))


all:
	for PY in *.py; do \
		[[ "$${PY}" != "main.py" ]] && mpremote fs cp "$${PY}" :$${PY}; \
	done

#go.py: $(ADDITIONAL_SOURCES)
#
#%.py:
#		mpremote fs cp $@ :$@

run:
	make all
	mpremote soft-reset
	mpremote run go.py
