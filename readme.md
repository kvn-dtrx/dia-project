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
    make install
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
# dia:end
```

Then:

```shell
dia                 # current directory
dia -n path/to/repo # dry-run
```

Shebang (if any) stays on line 1; the begin marker follows on line 2.

### Configuration

Default config ships in the repo (`src/dia_project/config.yaml`):

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
