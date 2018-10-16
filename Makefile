.PHONY: build

# test commands and arguments
tcommand = py.test -x
tmessy = -svv
targs = --cov-report term-missing --cov pgnotify

check: test fmt lint


pip:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

tox:
	tox

test:
	$(tcommand) $(targs)

stest:
	$(tcommand) $(tmessy) $(targs)

clean:
	git clean -fXd
	find . -name \*.pyc -delete

fmt:
	isort -rc .
	black . --exclude venv

lint:
	flake8 pgnotify
	flake8 tests

tidy: clean lint

all: pip lint tox

build:
	python setup.py sdist bdist_wheel --universal

upload:
	twine upload dist/*

publish: build upload
