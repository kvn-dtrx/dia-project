# ---
# description: >-
#   Embeds resource snippets into files at configurable markers
# ---

# ---

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from box import Box

from .utils import from_file

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".eggs",
}

SKIP_SUFFIXES = {
    ".7z",
    ".a",
    ".bin",
    ".bundle",
    ".class",
    ".db",
    ".dll",
    ".dylib",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".lz4",
    ".mozlz4",
    ".o",
    ".pdf",
    ".png",
    ".pyc",
    ".pyo",
    ".so",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
    ".tar",
    ".wasm",
    ".webp",
    ".woff",
    ".woff2",
    ".xz",
    ".zip",
}

TEXT_SAMPLE_BYTES = 8192
MARKER_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class IntegrityError(ValueError):
    """Raised when marker structure or snippet addressing is invalid."""


def process(session: Box) -> int:
    marker = get_marker(session)
    resources = get_resources_path(session)
    begin_re, end_re = compile_marker_patterns(marker)
    session.ephemeral.marker = marker
    session.ephemeral.resources_path = resources
    session.ephemeral.begin_re = begin_re
    session.ephemeral.end_re = end_re
    session.ephemeral.begin_token = f"{marker}:begin"
    session.ephemeral.end_token = f"{marker}:end"

    if not resources.is_dir():
        logging.error(f"Resources directory does not exist:\n  {resources}")
        return 1

    logging.debug(f"Using resources:\n  {resources}")
    logging.debug(f"Using marker keyword:\n  {marker}")

    errors = 0
    directories: list[Path] = session.ephemeral.directories
    for directory in directories:
        base = Path(directory)
        logging.info(
            f"Scanning for {marker} markers under:\n  {base.resolve()}"
        )
        for path in iter_candidate_files(base):
            if not process_file(session, path):
                errors += 1
    return errors


def get_marker(session: Box) -> str:
    marker = str(session.general.get("marker") or "dia").strip()
    if not marker or not MARKER_NAME_RE.fullmatch(marker):
        raise IntegrityError(
            "general.marker must match "
            f"{MARKER_NAME_RE.pattern!r} (got {marker!r})"
        )
    return marker


def ensure_xdg_data_home() -> None:
    """Apply the XDG Base Directory default when XDG_DATA_HOME is unset."""
    if not os.environ.get("XDG_DATA_HOME"):
        os.environ["XDG_DATA_HOME"] = str(Path.home() / ".local" / "share")


def get_resources_path(session: Box) -> Path:
    raw = session.general.get("resources")
    if raw in (None, ""):
        raise IntegrityError(
            "general.resources is required and must be an absolute path "
            "(shell variables like $HOME / ${XDG_DATA_HOME} are expanded)"
        )

    ensure_xdg_data_home()
    expanded = os.path.expandvars(str(raw).strip())
    path = Path(expanded).expanduser()

    if "$" in expanded or (expanded.startswith("~") and not path.is_absolute()):
        raise IntegrityError(
            "general.resources still contains unresolved shell variables:\n"
            f"  {raw!r} → {expanded!r}"
        )
    if not path.is_absolute():
        raise IntegrityError(
            "general.resources must be an absolute path after expansion:\n"
            f"  {raw!r} → {path}"
        )
    return path.resolve()


def compile_marker_patterns(marker: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    escaped = re.escape(marker)
    begin_re = re.compile(
        rf"^(?P<indent>\s*)(?P<open><!--\s*|#\s*|//\s*|;\s*)?"
        rf"{escaped}:begin\s+(?P<path>\S+)"
        rf"(?P<close>\s*-->)?\s*$"
    )
    end_re = re.compile(
        rf"^(?P<indent>\s*)(?P<open><!--\s*|#\s*|//\s*|;\s*)?"
        rf"{escaped}:end"
        rf"(?P<close>\s*-->)?\s*$"
    )
    return begin_re, end_re


def iter_candidate_files(base: Path) -> list[Path]:
    base = base.resolve()
    if base.is_file():
        return [base] if _is_candidate_file(base) else []

    found: list[Path] = []
    if not base.is_dir():
        logging.error(f"Not a file or directory:\n  {base}")
        return found

    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(
            d
            for d in dirnames
            if d not in SKIP_DIR_NAMES and not d.endswith(".egg-info")
        )
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if _is_candidate_file(path):
                found.append(path)
    return found


def _is_candidate_file(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    if path.name == ".DS_Store":
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    return _is_text_file(path)


def _is_text_file(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            sample = handle.read(TEXT_SAMPLE_BYTES)
    except OSError:
        return False
    if b"\x00" in sample:
        return False
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def process_file(session: Box, path: Path) -> bool:
    """Process one file. Returns False on integrity failure."""
    original = from_file(path)
    if original is None:
        return True
    if (
        session.ephemeral.begin_token not in original
        and session.ephemeral.end_token not in original
    ):
        return True

    try:
        updated, regions = embed_regions(session, original, path)
    except IntegrityError as e:
        logging.error(f"Integrity check failed in {path}:\n  {e}")
        return False

    if regions == 0:
        return True

    if updated == original:
        logging.info(f"Unchanged ({regions} region(s)):\n  {path}")
        return True

    if session.ephemeral.dry_run:
        logging.info(f"Would embed {regions} region(s) into:\n  {path}")
        return True

    try:
        path.write_text(updated, encoding="utf-8")
        logging.info(f"Embedded {regions} region(s) into:\n  {path}")
    except OSError as e:
        logging.error(f"Failed to write {path}:\n  {e}")
        return False
    return True


def embed_regions(
    session: Box, text: str, file_path: Path
) -> tuple[str, int]:
    begin_re: re.Pattern[str] = session.ephemeral.begin_re
    end_re: re.Pattern[str] = session.ephemeral.end_re
    marker: str = session.ephemeral.marker

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    regions = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        logical = _logical_line(line)
        begin = begin_re.match(logical)
        end = end_re.match(logical)

        if end is not None:
            raise IntegrityError(
                f"orphaned {marker}:end at line {i + 1}"
            )

        if begin is None:
            out.append(line)
            i += 1
            continue

        snippet_rel = begin.group("path")
        if snippet_rel in {".", "/"} or snippet_rel.endswith("/"):
            raise IntegrityError(
                f"invalid snippet path {snippet_rel!r} at line {i + 1}"
            )

        out.append(line)
        j = i + 1
        closed = False
        while j < len(lines):
            candidate = _logical_line(lines[j])
            if begin_re.match(candidate) is not None:
                raise IntegrityError(
                    f"nested {marker}:begin at line {j + 1} "
                    f"(open region: {snippet_rel})"
                )
            if end_re.match(candidate) is not None:
                snippet = load_snippet(session, snippet_rel, file_path)
                out.append(_ensure_trailing_newline(snippet))
                out.append(lines[j])
                regions += 1
                i = j + 1
                closed = True
                break
            j += 1

        if not closed:
            raise IntegrityError(
                f"unclosed {marker}:begin {snippet_rel} at line {i + 1}"
            )

    return "".join(out), regions


def _logical_line(line: str) -> str:
    return line.rstrip("\r\n")


def _ensure_trailing_newline(text: str) -> str:
    if text == "" or text.endswith("\n"):
        return text
    return text + "\n"


def load_snippet(session: Box, rel_path: str, file_path: Path) -> str:
    resources_root: Path = session.ephemeral.resources_path

    if rel_path.startswith("/") or rel_path.startswith("~"):
        raise IntegrityError(
            f"snippet path must be relative to resources/: {rel_path}"
        )
    parts = Path(rel_path).parts
    if ".." in parts:
        raise IntegrityError(
            f"snippet path must not contain '..': {rel_path}"
        )

    source = (resources_root / rel_path).resolve()
    if not source.is_relative_to(resources_root):
        raise IntegrityError(
            f"snippet path escapes resources/: {rel_path}"
        )
    if not source.is_file():
        raise IntegrityError(
            f"snippet not found for {file_path}:\n"
            f"  {rel_path}\n  ({source})"
        )
    if not _is_text_file(source):
        raise IntegrityError(
            f"snippet is not a UTF-8 text file:\n  {rel_path}"
        )

    content = from_file(source)
    if content is None:
        raise IntegrityError(f"could not read snippet: {rel_path}")
    return content
