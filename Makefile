# Makefile for constructing RPMs.
# Try "make" (for SRPMS) or "make rpm"

NAME = python-errata-tool
VERSION := $(shell PYTHONPATH=. python -c \
             'import errata_tool; print errata_tool.__version__')

all: srpm

clean:
	rm -rf dist/
	rm -rf errata-tool-$(VERSION).tar.gz
	rm -rf $(NAME)-$(VERSION)-1.el7.src.rpm

dist:
	python setup.py sdist \
	  && mv dist/errata-tool-$(VERSION).tar.gz .

srpm: dist
	fedpkg --dist epel7 srpm

rpm: dist
	mock -r epel-7-x86_64 rebuild $(NAME)-$(VERSION)-1.el7.src.rpm

.PHONY: dist rpm srpm
