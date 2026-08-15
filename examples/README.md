# Example snippets for dia

Tiny stand-ins for the real library ([dia-resources](https://github.com/kvn-dtrx/dia-resources)).
Used by unit tests and as documentation fixtures — not as `general.resources` in normal use.

```text
examples/
  gitignore/demo.ignore   # region embed (begin/end)
  scripts/hello.sh        # region embed
  scripts/whole.sh        # whole-file embed (dia:file; includes shebang)
```

Production embeds resolve against `${XDG_DATA_HOME}/dia/resources` (see dia config).
