#!/usr/bin/env sh

# ---
# description: |
#   Runs the following binary using its virtual environment:
#     __main__.py from https://github.com/kvn-dtrx/dia-project/src/dia_project
# ---

# ---

script="$(realpath "${0}")"
dir="$(dirname "${script}")"
project="$(git -C "${dir}" rev-parse --show-toplevel)"

exec \
    "${project}/.venv/bin/python" \
    -m dia_project \
    "${@}"
