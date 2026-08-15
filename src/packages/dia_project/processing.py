# ---
# description: >-
#   Embeds resource snippets into files at configurable markers
#   (region: begin/end; whole-file: file)
# ---

# ---


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
    file_re = compile_file_pattern(marker)
    session.ephemeral.marker = marker
    session.ephemeral.resources_path = resources
    session.ephemeral.begin_re = begin_re
    session.ephemeral.end_re = end_re
    session.ephemeral.file_re = file_re
    session.ephemeral.begin_token = f"{marker}:begin"
    session.ephemeral.end_token = f"{marker}:end"
    session.ephemeral.file_token = f"{marker}:file"

    if not resources.is_dir():
        logging.error(f"Resources directory does not exist:\n  {resources}")
        return 1

    logging.debug(f"Using resources:\n  {resources}")
    logging.debug(f"Using marker keyword:\n  {marker}")

    errors = 0
    directories: list[Path] = session.ephemeral.directories
    for directory in directories:
        base = Path(directory)
        logging.info(f"Scanning for {marker} markers under:\n  {base.resolve()}")
        for path in iter_candidate_files(base):
            if not process_file(session, path):
                errors += 1
    return errors


def get_marker(session: Box) -> str:
    marker = str(session.general.get("marker") or "dia").strip()
    if not marker or not MARKER_NAME_RE.fullmatch(marker):
        raise IntegrityError(
            f"general.marker must match {MARKER_NAME_RE.pattern!r} (got {marker!r})"
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


def compile_file_pattern(marker: str) -> re.Pattern[str]:
    escaped = re.escape(marker)
    return re.compile(
        rf"^(?P<indent>\s*)(?P<open><!--\s*|#\s*|//\s*|;\s*)?"
        rf"{escaped}:file\s+(?P<path>\S+)"
        rf"(?P<close>\s*-->)?\s*$"
    )


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

    # Cheap gate: mention of marker tokens anywhere (including prose/comments).
    if (
        session.ephemeral.begin_token not in original
        and session.ephemeral.end_token not in original
        and session.ephemeral.file_token not in original
    ):
        return True

    try:
        has_file = _has_marker_line(original, session.ephemeral.file_re)
        has_begin = _has_marker_line(original, session.ephemeral.begin_re)
        has_end = _has_marker_line(original, session.ephemeral.end_re)
        if has_file and (has_begin or has_end):
            raise IntegrityError(
                f"{session.ephemeral.file_token} cannot be combined with "
                f"{session.ephemeral.begin_token} / {session.ephemeral.end_token}"
            )
        if has_file:
            updated, regions = embed_file(session, original, path)
            unit = "file"
        else:
            updated, regions = embed_regions(session, original, path)
            unit = "region"
    except IntegrityError as e:
        logging.error(f"Integrity check failed in {path}:\n  {e}")
        return False

    if regions == 0:
        return True

    if updated == original:
        logging.info(f"Unchanged ({regions} {unit}(s)):\n  {path}")
        return True

    if session.ephemeral.dry_run:
        logging.info(f"Would embed {regions} {unit}(s) into:\n  {path}")
        return True

    try:
        path.write_text(updated, encoding="utf-8")
        logging.info(f"Embedded {regions} {unit}(s) into:\n  {path}")
    except OSError as e:
        logging.error(f"Failed to write {path}:\n  {e}")
        return False
    return True


def _has_marker_line(text: str, pattern: re.Pattern[str]) -> bool:
    for line in text.splitlines():
        if pattern.match(line) is not None:
            return True
    return False


def embed_file(session: Box, text: str, file_path: Path) -> tuple[str, int]:
    """Replace the whole host body from a single ``marker:file`` directive."""
    file_re: re.Pattern[str] = session.ephemeral.file_re
    marker: str = session.ephemeral.marker

    lines = text.splitlines(keepends=True)
    matches: list[tuple[int, re.Match[str], str]] = []
    for i, line in enumerate(lines):
        match = file_re.match(_logical_line(line))
        if match is not None:
            matches.append((i, match, line))

    if not matches:
        return text, 0
    if len(matches) > 1:
        raise IntegrityError(
            f"multiple {marker}:file markers "
            f"(lines {', '.join(str(i + 1) for i, _, _ in matches)})"
        )

    index, match, marker_line = matches[0]
    snippet_rel = match.group("path")
    if snippet_rel in {".", "/"} or snippet_rel.endswith("/"):
        raise IntegrityError(
            f"invalid snippet path {snippet_rel!r} at line {index + 1}"
        )

    prefix = lines[:index]
    nonblank_prefix = [line for line in prefix if not _is_blank_line(line)]

    snippet = load_snippet(session, snippet_rel, file_path)
    shebang, body = _split_shebang(snippet)
    body = _strip_edge_blank_lines(body)

    if shebang is not None:
        if len(nonblank_prefix) > 1:
            raise IntegrityError(
                f"{marker}:file at line {index + 1}: only a shebang may "
                "precede the marker when the snippet has a shebang"
            )
        if len(nonblank_prefix) == 1 and not _is_shebang_line(nonblank_prefix[0]):
            raise IntegrityError(
                f"{marker}:file at line {index + 1}: content before the "
                "marker must be a shebang when the snippet has a shebang"
            )
        out: list[str] = [
            _ensure_trailing_newline(shebang),
            "\n",
        ]
        _append_marker_line(out, marker_line)
        if body:
            out.append(_ensure_trailing_newline(body))
        return _strip_trailing_blank_lines("".join(out)), 1

    if nonblank_prefix:
        raise IntegrityError(
            f"{marker}:file at line {index + 1}: snippet has no shebang, "
            "so the host may not have content before the marker"
        )
    out = []
    _append_marker_line(out, marker_line)
    if body:
        out.append(_ensure_trailing_newline(body))
    return _strip_trailing_blank_lines("".join(out)), 1


def embed_regions(session: Box, text: str, file_path: Path) -> tuple[str, int]:
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
            raise IntegrityError(f"orphaned {marker}:end at line {i + 1}")

        if begin is None:
            out.append(line)
            i += 1
            continue

        snippet_rel = begin.group("path")
        if snippet_rel in {".", "/"} or snippet_rel.endswith("/"):
            raise IntegrityError(
                f"invalid snippet path {snippet_rel!r} at line {i + 1}"
            )

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
                snippet = _strip_edge_blank_lines(snippet)
                _append_marker_line(out, line)
                if snippet:
                    out.append(_ensure_trailing_newline(snippet))
                _append_marker_line(out, lines[j])
                regions += 1
                i = j + 1
                # Drop host blanks that used to follow end; padding after
                # the end marker is already ensured by _append_marker_line.
                while i < len(lines) and _is_blank_line(lines[i]):
                    i += 1
                closed = True
                break
            j += 1

        if not closed:
            raise IntegrityError(
                f"unclosed {marker}:begin {snippet_rel} at line {i + 1}"
            )

    # Marker padding adds a blank after each end; drop surplus blanks at EOF.
    return _strip_trailing_blank_lines("".join(out)), regions


def normalize_marker_spacing(text: str, marker: str = "dia") -> str:
    """Ensure exactly one blank line before and after each marker line.

    Does not load or rewrite snippet bodies — only spacing around
    ``<marker>:begin`` / ``<marker>:end`` lines. Idempotent.
    """
    begin_re, end_re = compile_marker_patterns(marker)
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        logical = _logical_line(lines[i])
        if begin_re.match(logical) is not None or end_re.match(logical) is not None:
            _append_marker_line(out, lines[i])
            i += 1
            while i < len(lines) and _is_blank_line(lines[i]):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return _strip_trailing_blank_lines("".join(out))


def _is_shebang_line(line: str) -> bool:
    return _logical_line(line).startswith("#!")


def _split_shebang(text: str) -> tuple[str | None, str]:
    """Return ``(shebang_line_without_newline, rest)`` if text starts with #!."""
    lines = text.splitlines(keepends=True)
    if not lines:
        return None, ""
    if not _is_shebang_line(lines[0]):
        return None, text
    return _logical_line(lines[0]), "".join(lines[1:])


def _append_marker_line(out: list[str], marker_line: str) -> None:
    """Append a marker with exactly one blank line before and after."""
    while out and _is_blank_line(out[-1]):
        out.pop()
    if out:
        out.append("\n")
    out.append(marker_line if marker_line.endswith("\n") else marker_line + "\n")
    out.append("\n")


def _logical_line(line: str) -> str:
    return line.rstrip("\r\n")


def _is_blank_line(line: str) -> bool:
    return _logical_line(line) == ""


def _strip_edge_blank_lines(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _ensure_trailing_newline(text: str) -> str:
    if text == "" or text.endswith("\n"):
        return text
    return text + "\n"


def _strip_trailing_blank_lines(text: str) -> str:
    """Drop extra blank lines at EOF; keep a single terminating newline."""
    if text == "":
        return text
    lines = text.splitlines(keepends=True)
    while lines and _is_blank_line(lines[-1]):
        lines.pop()
    if not lines:
        return "\n"
    return _ensure_trailing_newline("".join(lines))


def load_snippet(session: Box, rel_path: str, file_path: Path) -> str:
    resources_root: Path = session.ephemeral.resources_path

    if rel_path.startswith("/") or rel_path.startswith("~"):
        raise IntegrityError(f"snippet path must be relative to resources/: {rel_path}")
    parts = Path(rel_path).parts
    if ".." in parts:
        raise IntegrityError(f"snippet path must not contain '..': {rel_path}")

    source = (resources_root / rel_path).resolve()
    if not source.is_relative_to(resources_root):
        raise IntegrityError(f"snippet path escapes resources/: {rel_path}")
    if not source.is_file():
        raise IntegrityError(
            f"snippet not found for {file_path}:\n  {rel_path}\n  ({source})"
        )
    if not _is_text_file(source):
        raise IntegrityError(f"snippet is not a UTF-8 text file:\n  {rel_path}")

    content = from_file(source)
    if content is None:
        raise IntegrityError(f"could not read snippet: {rel_path}")
    return content
