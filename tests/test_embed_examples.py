# ---
# title: Embed tests against examples/
# ---

# ---

from __future__ import annotations

from pathlib import Path

import pytest
from box import Box

from dia_project.bootstrap import EXAMPLES_DIR
from dia_project.processing import (
    compile_marker_patterns,
    embed_regions,
    get_resources_path,
    process,
)


def _session_for_examples(tmp_path: Path) -> Box:
    marker = "dia"
    begin_re, end_re = compile_marker_patterns(marker)
    session = Box(default_box=True)
    session.general.resources = str(EXAMPLES_DIR.resolve())
    session.general.marker = marker
    session.ephemeral.directories = [tmp_path]
    session.ephemeral.dry_run = False
    session.ephemeral.marker = marker
    session.ephemeral.resources_path = EXAMPLES_DIR.resolve()
    session.ephemeral.begin_re = begin_re
    session.ephemeral.end_re = end_re
    session.ephemeral.begin_token = f"{marker}:begin"
    session.ephemeral.end_token = f"{marker}:end"
    return session


def test_examples_dir_exists() -> None:
    assert EXAMPLES_DIR.is_dir()
    assert (EXAMPLES_DIR / "gitignore" / "demo.ignore").is_file()
    assert (EXAMPLES_DIR / "scripts" / "hello.sh").is_file()


def test_xdg_data_home_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    session = Box(default_box=True)
    session.general.resources = "${XDG_DATA_HOME}/dia/resources"
    path = get_resources_path(session)
    assert path == (
        Path.home() / ".local" / "share" / "dia" / "resources"
    ).resolve()


def test_embed_hello_snippet(tmp_path: Path) -> None:
    session = _session_for_examples(tmp_path)
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/bin/sh\n# dia:begin scripts/hello.sh\n# dia:end\n",
        encoding="utf-8",
    )
    updated, n = embed_regions(session, target.read_text(encoding="utf-8"), target)
    assert n == 1
    assert "printf 'hello from dia examples" in updated
    assert updated.startswith("#!/bin/sh\n")
    # Idempotent
    again, n2 = embed_regions(session, updated, target)
    assert n2 == 1
    assert again == updated


def test_embed_gitignore_demo(tmp_path: Path) -> None:
    session = _session_for_examples(tmp_path)
    target = tmp_path / ".gitignore"
    target.write_text(
        "# dia:begin gitignore/demo.ignore\n# dia:end\n",
        encoding="utf-8",
    )
    updated, n = embed_regions(session, target.read_text(encoding="utf-8"), target)
    assert n == 1
    assert "*.demo-cache/" in updated


def test_process_writes_file(tmp_path: Path) -> None:
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/bin/sh\n# dia:begin scripts/hello.sh\n# dia:end\n",
        encoding="utf-8",
    )
    session = Box(default_box=True)
    session.general.resources = str(EXAMPLES_DIR.resolve())
    session.general.marker = "dia"
    session.ephemeral.directories = [tmp_path]
    session.ephemeral.dry_run = False
    assert process(session) == 0
    text = target.read_text(encoding="utf-8")
    assert "hello from dia examples" in text
    assert process(session) == 0  # idempotent
