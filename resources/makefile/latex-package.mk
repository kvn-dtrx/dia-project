PACKAGE_NAME := $(shell basename "$$PWD")
STYLES := $(wildcard styles/*.sty)
CLASSES := $(wildcard classes/*.cls)
CONFIGS := $(wildcard configs/*.cfg.sty)
FILES := $(CLASSES) $(STYLES) $(CONFIGS)

UNAME_S := $(shell uname -s)
ifeq ($(TEXMF),)
    ifeq ($(UNAME_S),Darwin)
        TEXMF := $(HOME)/Library/texmf
    else
        TEXMF := $(HOME)/texmf
    endif
endif

TARGET = $(TEXMF)/tex/latex/$(PACKAGE_NAME)

.PHONY: help install uninstall

help: ## Shows this help
	@echo "Available targets for make:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-13s: %s\n", $$1, $$2}'

install: ## Installs package to TEXMF
	mkdir -p $(TARGET)
	@for file in $(FILES); do \
		ln -sf "$$(realpath $$file)" "$(TARGET)/$$(basename $$file)"; \
	done
# 	Not strictly necessary; however, it does not harm.
	texhash "$(TEXMF)"

uninstall: ## Removes package from TEXMF
	@for file in $(FILES); do \
		rm -f "$(TARGET)/$$(basename $$file)"; \
	done
# 	Not strictly necessary; however, it does not harm.
	texhash $(TEXMF)
