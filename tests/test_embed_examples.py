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
    IntegrityError,
    compile_file_pattern,
    compile_marker_patterns,
    embed_file,
    embed_regions,
    get_resources_path,
    normalize_marker_spacing,
    process,
)


def _session_for_examples(tmp_path: Path) -> Box:
    marker = "dia"
    begin_re, end_re = compile_marker_patterns(marker)
    file_re = compile_file_pattern(marker)
    session = Box(default_box=True)
    session.general.resources = str(EXAMPLES_DIR.resolve())
    session.general.marker = marker
    session.ephemeral.directories = [tmp_path]
    session.ephemeral.dry_run = False
    session.ephemeral.marker = marker
    session.ephemeral.resources_path = EXAMPLES_DIR.resolve()
    session.ephemeral.begin_re = begin_re
    session.ephemeral.end_re = end_re
    session.ephemeral.file_re = file_re
    session.ephemeral.begin_token = f"{marker}:begin"
    session.ephemeral.end_token = f"{marker}:end"
    session.ephemeral.file_token = f"{marker}:file"
    return session


def test_examples_dir_exists() -> None:
    assert EXAMPLES_DIR.is_dir()
    assert (EXAMPLES_DIR / "gitignore" / "demo.ignore").is_file()
    assert (EXAMPLES_DIR / "scripts" / "hello.sh").is_file()
    assert (EXAMPLES_DIR / "scripts" / "whole.sh").is_file()


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
    assert updated.startswith("#!/bin/sh\n\n# dia:begin scripts/hello.sh\n\n")
    assert updated.rstrip().endswith("# dia:end")
    assert "\n\n# dia:end\n" in updated
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
    assert updated.startswith("# dia:begin gitignore/demo.ignore\n\n")
    assert "\n\n# dia:end\n" in updated
    # No surplus blank line after a terminal end marker
    assert updated.endswith("# dia:end\n")
    assert not updated.endswith("# dia:end\n\n")


def test_embed_strips_eof_blank_after_end(tmp_path: Path) -> None:
    session = _session_for_examples(tmp_path)
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/bin/sh\n# dia:begin scripts/hello.sh\n# dia:end\n\n\n",
        encoding="utf-8",
    )
    updated, n = embed_regions(session, target.read_text(encoding="utf-8"), target)
    assert n == 1
    assert updated.endswith("# dia:end\n")
    assert not updated.endswith("\n\n")


def test_normalize_marker_spacing_idempotent() -> None:
    raw = (
        "#!/bin/sh\n"
        "# dia:begin scripts/hello.sh\n"
        "echo hi\n"
        "# dia:end\n"
        "tail\n"
    )
    once = normalize_marker_spacing(raw)
    assert once == (
        "#!/bin/sh\n"
        "\n"
        "# dia:begin scripts/hello.sh\n"
        "\n"
        "echo hi\n"
        "\n"
        "# dia:end\n"
        "\n"
        "tail\n"
    )
    assert normalize_marker_spacing(once) == once


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
    assert "\n\n# dia:begin scripts/hello.sh\n\n" in text
    assert process(session) == 0  # idempotent


def test_embed_file_whole_snippet(tmp_path: Path) -> None:
    session = _session_for_examples(tmp_path)
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/usr/bin/env sh\n\n# dia:file scripts/whole.sh\n",
        encoding="utf-8",
    )
    updated, n = embed_file(session, target.read_text(encoding="utf-8"), target)
    assert n == 1
    assert updated.startswith(
        "#!/usr/bin/env sh\n\n# dia:file scripts/whole.sh\n\n"
    )
    assert "whole-file hello from dia examples" in updated
    assert "dia:begin" not in updated
    assert "dia:end" not in updated
    again, n2 = embed_file(session, updated, target)
    assert n2 == 1
    assert again == updated


def test_embed_file_uses_snippet_shebang(tmp_path: Path) -> None:
    session = _session_for_examples(tmp_path)
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/bin/sh\n\n# dia:file scripts/whole.sh\n",
        encoding="utf-8",
    )
    updated, n = embed_file(session, target.read_text(encoding="utf-8"), target)
    assert n == 1
    assert updated.startswith("#!/usr/bin/env sh\n")


def test_embed_file_rejects_begin_combo(tmp_path: Path) -> None:
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/usr/bin/env sh\n\n# dia:file scripts/whole.sh\n"
        "# dia:begin scripts/hello.sh\n# dia:end\n",
        encoding="utf-8",
    )
    session = Box(default_box=True)
    session.general.resources = str(EXAMPLES_DIR.resolve())
    session.general.marker = "dia"
    session.ephemeral.directories = [tmp_path]
    session.ephemeral.dry_run = False
    assert process(session) == 1


def test_embed_file_allows_begin_mention_in_prose(tmp_path: Path) -> None:
    """Comments mentioning begin/end must not trip the file/region conflict."""
    session = _session_for_examples(tmp_path)
    target = tmp_path / "tool.sh"
    target.write_text(
        "#!/usr/bin/env sh\n\n# dia:file scripts/whole.sh\n\n"
        "# Note: older hosts used dia:begin / dia:end region markers.\n",
        encoding="utf-8",
    )
    assert process(session) == 0
    text = target.read_text(encoding="utf-8")
    assert "# dia:file scripts/whole.sh" in text
    assert "whole-file hello from dia examples" in text
    assert process(session) == 0


def test_embed_file_rejects_content_before_marker(tmp_path: Path) -> None:
    session = _session_for_examples(tmp_path)
    target = tmp_path / "tool.sh"
    with pytest.raises(IntegrityError, match="only a shebang"):
        embed_file(
            session,
            "#!/usr/bin/env sh\necho x\n\n# dia:file scripts/whole.sh\n",
            target,
        )
