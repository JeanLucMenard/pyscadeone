# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
# 
# use: 'make help', or 'make' for targets help
# ==============================================================

.PHONY: help _venv _dependencies setup
.PHONY: _codespell _flake8 checks tests is_smoke
.PHONY: build html distrib
.PHONY: clean clobber version

SHELL:= bash

# ----------------------------------------
# Python environments
#
PYTHON ?= python
VENV ?= .venv

ACTIVATE = source scripts/activate.sh $(VENV)

# ----------------------------------------
# Checks
#
# Directories for flake8 and codespell
CHECK_DIRS := src tests doc 
# flit option. Default: check for uncommitted files
FLIT_NO_USE_VCS := --no-use-vcs
FLIT_OPTS ?= $(FLIT_NO_USE_VCS)

# Variables
VERSION := $(shell sed -ne 's/__version__ = "\(.*\)"/\1/p' src/ansys/scadeone/__init__.py)
DISTRIB := ansys_scadeone-$(VERSION)

# ----------------------------------------
# Rules

# Entry point
all: help
	@echo; echo "pyscadeone version:" $(VERSION)

#help: Please use 'make target' where target is one of
help: 
	@sed -n \
	-e '/^#help:/{ s/#help: *//' \
	-e 's/$$(PYTHON)/$(PYTHON)/' \
	-e 's/$$(VENV)/$(VENV)/' \
	-e 'p }' Makefile

#help: version    scadeone version from __init__.py
version:
	@echo $(VERSION)


# ----------------------------------------
# Setup Rules

#help:
#help:            --- Setup ---
#help: setup      to make python virtual environment and
#help:            packages installation with optional settings:
#help:                - PYTHON=<python path> (default: $(PYTHON))
#help:                - VENV=<subfolder> (default: $(VENV))
setup: _venv _dependencies


# internal target - create virtual environment according to PYTHON and VENV vars
_venv: 
	@echo "--- Setting up virtual environment"
	@"$(SHELL)" scripts/setup.sh $(VENV) "$(PYTHON)"
 
# internal target - Calls flit for dependencies
_dependencies: 
	@echo "--- Installing dependencies"
	@ $(ACTIVATE); \
      flit install --only-deps


# ----------------------------------------
# Check Rules

#help:
#help:            --- After setup ---
#help: checks     to make flake8 and codespell checks
checks: _codespell _flake8


_codespell: # internal - Calls codespell
	@echo "--- Code spelling"
	@$(ACTIVATE); codespell $(CHECK_DIRS) --toml pyproject.toml 

_flake8: # internal - Calls flake8
	@echo "--- Code format check"
	@$(ACTIVATE); for d in $(CHECK_DIRS); do flake8 $$d ; done

# ----------------------------------------
# Build Rules

#help: html       to make html documentation
html:
	@echo "--- HTML documentation in doc/_build/html"
	@$(ACTIVATE); sphinx-build.exe -M html doc/source doc/_build -j auto

#help: autodoc    documentation auto-build with browser updates
autodoc:
	@$(ACTIVATE); sphinx-autobuild.exe --open-browser --watch src doc/source doc/_build/html


#help:link       list sphinx generated links
links:
	@$(ACTIVATE); python -m sphinx.ext.intersphinx doc/_build/objects.inv > links.txt
	@echo "--- Check: links.txt"

#help: build      to build the package. Check FLIT_OPT for flit version control checks
build:
	@echo "--- Package creation in ./dist"
	@$(ACTIVATE); flit build $(FLIT_OPTS)

#help: distrib    to make package and documentation distribution in ./dist
#help:            Rely on 'build' and 'html' targets
distrib: build html
	@echo "--- Distribution"
	@"$(SHELL)" scripts/distrib.sh $(VENV) $(DISTRIB)


# ----------------------------------------
# Test Rules

#help: tests      to run unit tests
tests:
	@echo "--- Running unit tests"
	@$(ACTIVATE); pytest

#help: is_smoke   to make smoke test. Recommended after 'distrib',
#help:            to use the package
# This rule creates a new environment, installs the built package
# and run the smoke test
is_smoke:
	@echo "--- Smoke test"
	@$(SHELL) scripts/smoke_test.sh $(VENV) $(DISTRIB)

# ----------------------------------------
# Cleaning Rules

#help:
#help:            --- Specials ---
#help: clean      to clean ./dist folder
clean:
	rm -rf dist/*

#help: clobber    to clean ./dist folder and to remove $(VENV)
clobber: clean
	@ read -p "Removing $(VENV) [y/n]:" ; \
	if [ "$$REPLY" = "y" ] ; \
	then rm -rf $(VENV) ; \
	fi

