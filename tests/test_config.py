# ---
# title: Config loading (default + DIA_CONF overrides)
# ---

from __future__ import annotations

from pathlib import Path

import pytest

from dia_project.bootstrap import DIA_CONF_ENV, resolve_user_config_path
from dia_project.utils import load_config


def test_resolve_user_config_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DIA_CONF_ENV, raising=False)
    assert resolve_user_config_path() == Path.home() / ".config" / "dia.conf"


def test_resolve_user_config_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    conf = tmp_path / "custom.conf"
    monkeypatch.setenv(DIA_CONF_ENV, str(conf))
    assert resolve_user_config_path() == conf


def test_load_config_merges_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    conf = tmp_path / "dia.conf"
    conf.write_text(
        "general:\n  marker: custom\n  log_level: DEBUG\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(DIA_CONF_ENV, str(conf))
    session = load_config()
    assert session.general.marker == "custom"
    assert session.general.log_level == "DEBUG"
    # resources still from default unless overridden
    assert "dia/resources" in str(session.general.resources)


def test_load_config_missing_override_ok(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(DIA_CONF_ENV, str(tmp_path / "missing.conf"))
    session = load_config()
    assert session.general.marker == "dia"
