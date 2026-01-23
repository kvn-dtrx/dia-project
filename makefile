# ---
# title: Makefile for dia-project
# ---

# ---

PYTHON_VERSION := 3.11.3
VENV ?= .venv
XDG_BIN_HOME ?= $(HOME)/.local/bin

TARGETS := help install dev reset
.PHONY: $(TARGETS)

_help: ## Displays available targets with description
	@scripts/make-help.sh

setup: ## Links binaries
	ln -sf "$(CURDIR)/scripts/invoke.sh" "$(XDG_BIN_HOME)/dia"
	chmod +x "$(XDG_BIN_HOME)/dia"
# TODO: Provide a cp and an ln-s option

apply: ## Installs the module and creates a symlink to a directory in the PATH
	pyenv local $(PYTHON_VERSION)
	python -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e .

install: setup apply ## Runs setup and apply

# # dev: install ## Executes `install` and sets up additional development tools
# 	$(VENV)/bin/python -m pip install -e .[dev]
# 	$(VENV)/bin/pre-commit install

clear: ## Clears cache files
	find . -type d -iname "__pycache__" | xargs rm -rf --

reset: clear ## Clears all build artefacts and removes the virtual environment
	find . -type d -iname "*.egg-info" | xargs rm -rf --
	rm -rf $(VENV)
	pyenv local --unset
