# Dia-Project

## Synopsis

Dia embeds shared snippets into project files at `dia:begin` / `dia:end`
markers. The production snippet library lives in a separate repository
([dia-resources](https://github.com/kvn-dtrx/dia-resources)); this repo is
the embed engine plus a tiny `examples/` tree for tests and illustration.

## Installation

### Requirements

- macOS/Linux
- Python 3.11+
- pyenv (optional, for the Makefile flow)

### Setup

1. Clone and install dia:

    ```shell
    git clone https://github.com/kvn-dtrx/dia-project.git
    cd dia-project
    make all
    ```

2. Clone the snippet library and wire it into the XDG data home:

    ```shell
    git clone https://github.com/kvn-dtrx/dia-resources.git
    cd dia-resources
    make install
    ```

   That creates `${XDG_DATA_HOME:-~/.local/share}/dia/resources` → the
   library’s `src/` tree (dia’s default `general.resources` path).

### Tests

```shell
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

Tests use `examples/` only; they do not require dia-resources.

## Usage

Mark a region and address a snippet path relative to the resources root:

```shell
#!/bin/sh

# dia:begin scripts/make-help.sh

# ---
# description: >-
#   Lists all make targets with description; more precisely, all lines
#   conceptually matching "identifier: ## description"
# ---

# ---

script="$(realpath "${0}")"
script_dir="$(dirname "${script}")"
ls_make_targets="${script_dir}/_ls-make-targets.awk"

printf "\n"
printf "\033[1;37m    %s\033[0m\n" "Available targets for make:"
printf "\n"

"${ls_make_targets}" Makefile | sed -e "s/^/    /"

printf "\n"
printf "\033[1;37m    %s\033[0m\n" "Important make flags:"
printf "\n"

printf "    %-16s: %s\n" \
    "-n" "Dry-run (print commands without running them)" \
    "-s" "Silent mode (don't print executed commands)" \
    "--debug[=b|v|a]" "Debug info (b=basic [default], v=verbose, a=all)"

# dia:end

```

Then:

```shell
dia                 # current directory
dia -n path/to/repo # dry-run
```

Shebang (if any) stays on line 1. Embed keeps exactly one blank line before
and after each `dia:begin` / `dia:end` marker.

### Configuration

Default config ships in the repo (`src/packages/dia_project/config.yaml`):

```yaml
general:
  resources: "${XDG_DATA_HOME}/dia/resources"
  marker: "dia"
```

Optional overrides (YAML, same shape) are merged on top:

- `$DIA_CONF` if set, else
- `~/.config/dia.conf` if that file exists

Missing override file is ignored. `XDG_DATA_HOME` defaults to `~/.local/share`
when unset.

### Examples

See [`examples/`](examples/) for minimal fixtures used by the test suite.

## Colophon

**Author:** [kvn-dtrx](https://github.com/kvn-dtrx)

**License:** [MIT License](license.txt)
