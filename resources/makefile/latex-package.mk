# ---
# title: Makefile for <name>
# ---

# ---

DST:=$(shell kpsewhich -var-value=TEXMFHOME)

.PHONY: help cp ln rm

help: ## Displays available targets with description
	@printf "Available targets for make:\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-13s: %s\n", $$1, $$2}'

cp: ## Copies package into TEXMF
	@mkdir -p $(DST)
	@for package in src/*/; do \
		cp -r "$${package}" "$(DST)/"; \
	done

ln: ## Symlinks package into TEXMF
	@mkdir -p $(DST)
	@for package in src/*/; do \
		ln -sf "$${package}" "$(DST)/"; \
	done

rm: ## Removes package from TEXMF
	@for package in $(PACKAGES); do \
		rm -r "$(DST)/$$(basename $$package)"; \
	done
