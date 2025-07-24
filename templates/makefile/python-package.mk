PIP := $(shell which pip3)

.PHONY: help apply unapply stub unstub install uninstall

help: ## Shows this help
	@echo "Available targets for make:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-13s: %s\n", $$1, $$2}'

apply: ## Installs the package in editable mode for the user
	$(PIP) install --user --editable . --break-system-packages

unapply: ## Uninstalls the package from the user environment
	$(PIP) uninstall -y pyutils

stub: ## Generates type stub files
	stubgen -o src src/pyutils

unstub: ## Removes previously generated stub files
	rm src/pyutils/*.pyi

install: ## Runs apply and stub
	@${MAKE} apply
	@${MAKE} stub

uninstall: ## Runs unapply and unstub
	@${MAKE} unapply
	@${MAKE} unstub