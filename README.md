# Dia-Project

## Synopsis

Dia embeds shared snippets into project files at `dia:begin` / `dia:end`
region markers or `dia:file` whole-file markers. The production snippet library
lives in a separate repository
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
   library’s `share/` tree (dia’s default `general.resources` path).

### Tests

```shell
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

Tests use `examples/` only; they do not require dia-resources.

## Usage

### Whole-file embeds (`dia:file`)

For hosts that should mirror an entire snippet (scripts with a shebang, full
Makefiles, warning banners, …), use a fixed three-line header when the
snippet starts with a shebang:

```shell
#!/usr/bin/env bash

# dia:file scripts/resolve-note.sh
```

Dia takes the shebang from the snippet (SoT), keeps the `dia:file` line, and
rewrites the rest of the host from the snippet body (everything after the
snippet shebang). Do not mix `dia:file` with `dia:begin` / `dia:end` in the
same file.

Snippets without a shebang use a leading `dia:file` line only:

```makefile
# dia:file makefile/latex-package.mk
```

### Region embeds (`dia:begin` / `dia:end`)

Mark a region and address a snippet path relative to the resources root:

```shell
#!/bin/sh

# dia:begin gitignore/demo.ignore

*.demo-cache/

# dia:end
```

Then:

```shell
dia                 # current directory
dia -n path/to/repo # dry-run
```

Region embeds keep exactly one blank line before and after each
`dia:begin` / `dia:end` marker. Whole-file embeds keep one blank line after
the `dia:file` marker (and after the shebang when present).

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
