# Dia Project

## Synopsis

This repository provides a convenient functionality to pull resources which are required across (*διά*) projects but cannot be incorporated via git submodules or subtrees such as files like `.gitignore` or `.pylintrc`.

Furthermore, a very small example library of such resources is included.

## Installation

### Requirements

- macOS/Linux (currently)
- Python 3.11
- pyenv

### Setup

1. Navigate to a working directory of your choice—such as `${XDG_DATA_HOME}`—then clone the repository and enter it:

    ``` shell
    git clone https://github.com/kvn-dtrx/dia-project.git &&
       cd dia-project
    ```

2. Choose a setup option ~~based on your operating system and~~ intended use. If you prefer to run the commands manually yourself or want to inspect what each make target does first, use the `-n` flag for a dry run. This prints the commands without executing them:

    ``` shell
    make -n <target>
    ```

## Usage

To synchronise shared project files from `dia-project` into another repository, follow these steps:

1. Create `.dia-pull.toml` manifests in your target repositories

   At the root of your target repository[^technically], create a file named `.dia-pull.toml` and specify the generic resources required for the project (the employed syntax will be exemplified below).

   [^technically]: Technically, this is not strictly necessary—but other choices would possibly undermine the idea of keeping project-related configurations close to the project.

2. Run the synchronisation binary

   The following command executes all pulling tasks which are specified in a `.dia-pull.toml` file subordinated to one of the directories `<dir_1>`, …, `<dir_N>`:

   ``` shell
   dia-pull <dir_1> … <dir_N>
   ```

   If no directory is specified, `dia-project` will operate only on the current working directory.

### Example

Let us consider a manifest located at `/path/to/project/.dia-pull.toml` with the following content:

```toml
# If the target is relative, it is interpreted with respect to `/path/to/resources/type/`.
[gitignore]
source = ["rust-basic"]
target = "foo/bar/.gitignore"

# When no target is specified, a sensible and not entirely arbitrary default is used.
[makefile]
source = ["latex-basic"]
# target = "makefile"

# One may even specify absolute paths in the source field.
[env]
source = ["/path/to/some/credential", "/path/to/another/credential"]
target = ".env"
```

Then, the following command pulls the specified resources for the project based at `/path/to/project/`:

```sh
dia-pull /path/to/project/
```

This command effects essentially:

``` shell
cat \
    "/path/to/resources/gitignores/rust-basic.txt" \
    !> "/path/to/target-repo/src/foo/.gitignore"

cat \
    "/path/to/resources/makefiles/latex-basic.mk" \
    !> "/path/to/target-repo/makefile"

cat \
    "/path/to/some/credential" "/path/to/another/credential" \
    !> "/path/to/target-repo/.env"
```

## Colophon

**Author:** [kvn-dtrx](https://github.com/kvn-dtrx)

**License:** [MIT License](license.txt)
