PYTHON_VERSION := 3.11.3
VENV := .venv
XDG_BIN_HOME ?= $(HOME)/.local/bin

BOLD_WHITE := \033[1;37m
RESET := \033[0m

TARGETS := help install dev reset
.PHONY: $(TARGETS)

help: ## Shows this help
	@echo
	@echo "    $(BOLD_WHITE)Available targets for make:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "    %-13s: %s\n", $$1, $$2}'
	@echo
	@echo "    $(BOLD_WHITE)Important Make Flags:$(RESET)"
	@echo "    -n              : Dry-run (print commands without running them)"
	@echo "    -s              : Silent mode (don't print executed commands)"
	@echo "    --debug[=b|v|a] : Debug info (b=basic [default], v=verbose, a=all)"
	@echo

setup: ## Links binaries
	ln -sf "$(CURDIR)/scripts/invoke.sh" "$(XDG_BIN_HOME)/dia"
	chmod +x "$(XDG_BIN_HOME)/dia"

apply: ## Installs the module and creates a symlink to a directory in the PATH
	pyenv local $(PYTHON_VERSION)
	python -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e .

install: ## Runs setup and apply
	@${MAKE} setup
	@${MAKE} apply

# # dev: ## Executes `install` and sets up additional development tools
# 	$(MAKE) install
# 	$(VENV)/bin/python -m pip install -e .[dev]
# 	$(VENV)/bin/pre-commit install

clear: ## Clears cache files
	find . -type d -name '__pycache__' | xargs rm -rf --

reset: ## Clears all build artifacts and removes the virtual environment
	$(MAKE) clear 
	find . -type d -name '*.egg-info' | xargs rm -rf --
	rm -rf $(VENV)
	pyenv local --unset
