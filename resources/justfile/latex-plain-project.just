# ---
# title: justfile for <name>
# ---

# ---

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

tex := "pdflatex"
main := "main"
style := "styles/styles.sty"
outdir := "target"

# Shows available recipes
default:
    @just --list --unsorted

# Builds the main PDF document
build: (outdir)
    {{tex}} -output-directory={{outdir}} {{main}}.tex
    {{tex}} -output-directory={{outdir}} {{main}}.tex

# Creates output directory if necessary
[private]
outdir:
    mkdir -p {{outdir}}
    touch {{outdir}}/.gitkeep

# Removes generated files except output files and .gitkeep
clean:
    find {{outdir}} -mindepth 1 \
        -not -iname "*.pdf" \
        -not -iname "*.png" \
        -not -iname "*.jpg" \
        -not -iname ".gitkeep" \
        -print0 | xargs -0 rm -rf --

# Removes all generated files including PDFs except .gitkeep
reset:
    find {{outdir}} -mindepth 1 \
        -not -iname ".gitkeep" \
        -print0 | xargs -0 rm -rf --

# Resets outputs and rebuilds everything
rebuild: reset build
