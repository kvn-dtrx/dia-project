# ---
# title: justfile for dia-project
# ---

# ---

#
# Convention: just = clear/reset ops; make = setup/install (bin link, venv).

# ---

venv := ".venv"

# Shows available recipes
default:
    @just --list --unsorted

# Clears __pycache__ directories
clear:
    find . -type d -iname "__pycache__" | xargs rm -rf --

# Clears caches, egg-info, and removes the virtual environment
reset: clear
    find . -type d -iname "*.egg-info" | xargs rm -rf --
    rm -rf {{venv}}
    pyenv local --unset
