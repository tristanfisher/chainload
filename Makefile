PYTHON ?= python
TEST=
PARAMETERS =

build:
	${PYTHON} setup.py build ${PARAMETERS}

test: build
	${PYTHON} setup.py test

tests: test
