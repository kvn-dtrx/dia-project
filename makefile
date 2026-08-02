# ---
# title: Makefile for dia-project
# ---

# ---

#
# Convention: make = setup/install (bin link, venv); clear/reset live in justfile.

# ---

PYTHON_VERSION := 3.11.3
VENV ?= .venv
XDG_BIN_HOME ?= $(HOME)/.local/bin

.PHONY: _help setup apply install test

_help: ## Displays available targets with description
	@bin/make-help.sh

setup: ## Links binaries
	ln -sf "$(CURDIR)/bin/invoke.sh" "$(XDG_BIN_HOME)/dia"
	chmod +x "$(XDG_BIN_HOME)/dia"
# TODO: Provide a cp and an ln-s option

apply: ## Installs the module and creates a symlink to a directory in the PATH
	pyenv local $(PYTHON_VERSION)
	python -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e .

install: setup apply ## Runs setup and apply

test: ## Runs the example-based test suite
	$(VENV)/bin/python -m pip install -e '.[dev]'
	$(VENV)/bin/pytest

# # dev: install ## Executes `install` and sets up additional development tools
# 	$(VENV)/bin/python -m pip install -e .[dev]
# 	$(VENV)/bin/pre-commit install
