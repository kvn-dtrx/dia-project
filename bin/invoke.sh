#!/usr/bin/env sh

# ---
# description: >-
#   Runs dia via the repository .venv (`python -m dia_project`)
# ---

# ---

script="$(realpath "${0}")"
dir="$(dirname "${script}")"
project="$(git -C "${dir}" rev-parse --show-toplevel)"

exec \
    "${project}/.venv/bin/python" \
    -m dia_project \
    "${@}"
