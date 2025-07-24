TEX=pdflatex
MAIN=main
STYLE=styles/styles.sty
OUTDIR=target

.PHONY: all clean cleanall rebuild

help: ## Shows this help
	@echo "Available targets for make:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-13s: %s\n", $$1, $$2}'

all: $(OUTDIR)/$(MAIN).pdf ## Builds the main pdf document

$(OUTDIR): ## Create output directory if necessary
	mkdir -p $(OUTDIR)
	touch $(OUTDIR)/.gitkeep

$(OUTDIR)/$(MAIN).pdf: $(MAIN).tex $(STYLE) | $(OUTDIR) ## Compiles the main LaTeX file twice
	$(TEX) -output-directory=$(OUTDIR) $(MAIN).tex
	$(TEX) -output-directory=$(OUTDIR) $(MAIN).tex

clean: ## Removes all generated files except pdfs and .gitkeep
	find $(OUTDIR) -mindepth 1 \
		-not -name '*.pdf' \
		-not -name '.gitkeep' \
		-print0 | xargs -0 rm -rf --

cleanall: ## Remove all generated files including pdfs except .gitkeep
	find $(OUTDIR) -mindepth 1 \
		-not -name '.gitkeep' \
		-print0 | xargs -0 rm -rf --

rebuild: ## Cleans all outputs and rebuild everything
	$(MAKE) cleanall
	$(MAKE) all
