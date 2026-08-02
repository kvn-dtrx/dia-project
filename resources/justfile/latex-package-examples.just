# ---
# title: justfile for <name>
# ---

# ---

examples := "examples"

# Shows available recipes
default:
    @just --list --unsorted

# Compiles examples via latexmk
compile:
    cd {{examples}} && latexmk

# Alias for compile
build: compile

# Removes intermediate compilation files
clean:
    cd {{examples}} && latexmk -c

# Full clean of examples
reset:
    cd {{examples}} && latexmk -C

# Resets and rebuilds examples
rebuild: reset build
