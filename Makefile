.PHONY: build
build:
	sphinx-build -b html docs/source/ docs/build/html
	python -m build
	twine check dist/*


.PHONY: clean
clean:
	rm -rf docs/build/html
	rm -rf dist
	rm -rf src/mkname.egg-info
	rm -rf tests/__pycache__
	rm -rf src/mkname/__pycache__
	rm -rf src/mkname/*.pyc


.PHONY: docs
docs:
	rm -rf docs/build/html
	sphinx-build -b doctest docs/source/ docs/build/html
	sphinx-build -b html docs/source/ docs/build/html


.PHONY: pre
pre:
	tox
	python precommit.py
	git status


.PHONY: test
test:
	python -m pytest


.PHONY: testv
testv:
	python -m pytest -vv
