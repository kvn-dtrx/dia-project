# ---
# title: justfile for <name>
# ---
#
# Convention: just = clear/reset ops; make = env/setup (venv, pip -e).

# ---

venv := ".venv"

# Shows available recipes
default:
    @just --list --unsorted

# Clear build artefacts (adapt paths as needed)
clear:
    find data -mindepth 1 ! -iname ".gitkeep" -delete
    find logs -mindepth 1 ! -iname ".gitkeep" -delete
    find plots -mindepth 1 ! -iname ".gitkeep" -delete

# Clear artefacts and remove virtual environment
reset: clear
    rm -rf {{venv}}
    pyenv local --unset
