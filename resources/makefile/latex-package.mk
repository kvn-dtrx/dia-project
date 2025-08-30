SRC := $(wildcard src/*)
PACKAGES := $(patsubst src/%,%,$(SRC))

UNAME_S := $(shell uname -s)
ifeq ($(TEXMF),)
    ifeq ($(UNAME_S),Darwin)
        TEXMF := $(HOME)/Library/texmf
    else
        TEXMF := $(HOME)/texmf
    endif
endif

TARGET = $(TEXMF)/tex/latex

.PHONY: help install uninstall

help: ## Shows this help
	@echo "Available targets for make:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-13s: %s\n", $$1, $$2}'

cp: ## Copies package into TEXMF
	@mkdir -p $(TARGET)
	@for package in $(PACKAGES); do \
		cp -r "$$(realpath src/$$package)" "$(TARGET)/"; \
	done
# 	Not strictly necessary; however, it does not harm.
	@texhash "$(TEXMF)"

ln: ## Symlinks package into TEXMF
	@mkdir -p $(TARGET)
	@for package in $(PACKAGES); do \
		ln -sf "$$(realpath src/$$package)" "$(TARGET)/"; \
	done
# 	Not strictly necessary; however, it does not harm.
	texhash "$(TEXMF)"

rm: ## Removes package from TEXMF
	@for package in $(PACKAGES); do \
		rm -r "$(TARGET)/$$(basename $$package)"; \
	done
# 	Not strictly necessary; however, it does not harm.
	texhash $(TEXMF)
