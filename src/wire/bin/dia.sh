#!/usr/bin/env sh

# ---
# title: Public shim for dia_project
# ---

# ---

script="$(realpath "${0}")"
dir="$(dirname "${script}")"
project="$(git -C "${dir}" rev-parse --show-toplevel)"

exec \
    "${project}/.venv/bin/python" \
    -m dia_project \
    "${@}"
