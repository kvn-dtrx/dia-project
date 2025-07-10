# Dia Project

## Synopsis

This repository provides a convenient functionality to pull resources which are required across (*διά*) projects but cannot be incorporated via git submodules or subtrees such as files like `.gitignore` or `.pylintrc`.

Furthermore, a very small example library of such resources is included.  

## Installation

## Usage

To synchronise shared project files from `dia-project` into another repository, follow these steps:

### 1. Create `.dia-pull.toml` manifests in your target repositories

At the root of your target repository[^technically], create a file named `.dia-pull.toml` and specify the generic resources required for the project (the employed syntax will be exemplified below).

[^technically]: Technically, this is not strictly necessary — but other choices would possibly undermine the idea of keeping project-related configurations close to the project …

### 2. Run the synchronisation binary

The following command executes all pulling tasks which are specified in a `.dia-pull.toml` file subordinated to one of the directories `<dir_1>`, …, `<dir_N>`:

``` shell
dia-project <dir_1> … <dir_N>
```

If no directory is specified, `dia-project` will operate only on the current working directory.

#### Example

Consider a `.dia-pull.toml` file with content:

```toml
[[gitignore]]
source = ["rust-basic"]
target = "foo/bar/.gitignore"

# When no target is specified, a (not so far-fetched) dault value is used.
[[makefile]]
source = ["latex-basic"]

# You can even specify absolute paths.
[[env]]
source = ["path/to/credential", "path/to/another/credential"]
target = ".env"
```

Note that no `target` is specified (points to default). This essentially runs:

``` shell
cat \
    "path/to/dia-project/gitignores/rust-basic.txt" \
    !> "path/to/target-repo/src/foo/.gitignore"

cat \
    "path/to/dia-project/makefiles/latex-basic.mk" \
    !> "path/to/target-repo/makefile"

cat \
    "path/to/credential" "path/to/another/credential" \
    !> "path/to/target-repo/.env"
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
