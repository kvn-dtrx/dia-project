# Dia Project

## Synopsis

This repository provides resources which are required across (*διά*) our projects (located at `~/data/projects`) and cannot be incorporated via git submodules or subtrees.

## Usage

To synchronise shared project files from `dia-project` into another repository, follow these steps:

### 1. Create a `.dia-pull` manifest in your target repository

At the root of your target repository, create a file named `.dia-pull`. This file should be written in POSIX `sh` syntax and specify:

- The path to the `dia-project` repository (typically relative).
- A list of files to copy.

#### Example

Consider a `.dia-pull.toml` file with content:

```toml
[[gitignore]]
source = ["rust-basic"]
target = "foo/bar/.gitignore"

[[makefile]]
source = ["latex-basic"]
```

Note that no `target` is specified (points to default). This essentially runs:

``` shell
cp \
    path/to/dia-project/gitignores/rust-basic.txt \
    path/to/target-repo/src/foo/.gitignore

cp \
    path/to/dia-project/makefiles/latex-basic.mk \
    path/to/target-repo/makefile
```

### 2. Run the synchronisation script

From the root of your target repository:

```sh
path/to/dia-project/script/sync-dia.sh
```

This will:

- Read the `.dia-pull` manifest.
- Copy the listed files from dia-project into the current repository.
- Overwrite existing files with the same name.

Optional Integration

You may optionally wrap sync-dia in a Makefile target or pre-commit hook for automation.
