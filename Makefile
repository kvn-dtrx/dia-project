# ---
# title: Makefile for dia-project
# ---

# ---

#
# Make targets follow paradigmata (setup / apply / install / all).
# Ops (clear/reset) live in justfile.

# ---

PYTHON_VERSION := 3.11.3
VENV ?= .venv
XDG_DATA_HOME ?= $(HOME)/.local/share
WIRE := $(CURDIR)/bin/make-wire.py

.PHONY: _help setup install all test

_help: ## Displays available targets with description
	@bin/make-help.sh

setup: ## Creates venv and installs the package editable
	pyenv local $(PYTHON_VERSION)
	python -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e .

install: ## Wire public shims (src/wire/bin → ~/.local/bin)
	@python3 "$(WIRE)" bin "$(CURDIR)"

all: setup install ## Runs setup and install

test: ## Runs the example-based test suite
	$(VENV)/bin/python -m pip install -e '.[dev]'
	$(VENV)/bin/pytest
