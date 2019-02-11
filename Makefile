.PHONY: build

# test commands and arguments
tcommand = py.test -x
tmessy = -svv
targs = --cov-report term-missing --cov pgnotify

check: fmt test lint

test:
	$(tcommand) $(targs)

stest:
	$(tcommand) $(tmessy) $(targs)

clean:
	find . -name \*.pyc -delete

fmt:
	isort -rc .
	black .

lint:
	flake8 pgnotify
	flake8 tests
