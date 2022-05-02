# Makefile for constructing RPMs.
# Try "make" (for SRPMS) or "make rpm"

NAME = python-errata-tool
VERSION := $(shell PYTHONPATH=. python -c \
             'import errata_tool; print(errata_tool.__version__)')
RELEASE := $(shell rpmspec \
             --define "dist .el7" \
             -q --srpm --qf "%{release}\n" python-errata-tool.spec)

all: srpm

clean:
	rm -rf dist/
	rm -rf errata-tool-$(VERSION).tar.gz
	rm -rf $(NAME)-$(VERSION)-$(RELEASE).src.rpm

dist:
	find errata_tool -name __pycache__ -o -name '*.pyc' | xargs rm -rf \
	  && python setup.py sdist --dist-dir .

srpm: dist
	fedpkg --release epel7 srpm

rpm: srpm
	mock -r epel-7-x86_64 rebuild $(NAME)-$(VERSION)-$(RELEASE).src.rpm

.PHONY: dist rpm srpm
