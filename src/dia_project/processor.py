# ---
# description: Provides the class DiaPullProcessor.
# ---

# ---


from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import logging
import tomli


class DiaPullProcessor:
    def __init__(
        self,
        shall_section_pass: Callable[[str], bool],
        ignore_base_dir: str = "_gitignore",
        log_level: int = logging.INFO,
        dry_run: bool = False,
    ) -> None:
        self.shall_section_pass = shall_section_pass
        self.ignore_base_dir = ignore_base_dir
        self.dry_run = dry_run
        self.setup_logging(log_level)

    @staticmethod
    def setup_logging(level: int) -> None:
        logging.basicConfig(
            level=level,
            format="%(levelname)s: %(message)s",
        )

    def process_section(
        self,
        toml_path: Path,
        section_name: str,
        section_entries: List[Dict[str, Any]],
        base_ignore_dir: Path,
    ) -> None:
        for entry in section_entries:
            sources = entry.get("source", [])
            target = entry.get("target")
            if not sources or not target:
                logging.warning(
                    "Skipping invalid %s entry in %s: missing source or target",
                    section_name,
                    toml_path,
                )
                continue

            combined_contents: List[str] = []
            for src in sources:
                source_file = base_ignore_dir / section_name / f"{src}.ignore"
                if source_file.exists() and source_file.is_file():
                    logging.debug(f"Reading source file: {source_file}")
                    try:
                        with source_file.open("r", encoding="utf-8") as f:
                            combined_contents.append(f.read())
                    except Exception as e:
                        logging.error(f"Failed to read {source_file}: {e}")
                else:
                    logging.warning(f"Source file not found: {source_file}")

            target_path = toml_path.parent / target
            target_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                with target_path.open("w", encoding="utf-8") as f:
                    f.write("\n".join(combined_contents))
                logging.info(f"Wrote combined {section_name} to: {target_path}")
            except Exception as e:
                logging.error(f"Failed to write {target_path}: {e}")

    def process_toml_file(self, toml_path: Path) -> None:
        try:
            with toml_path.open("rb") as f:
                config = tomli.load(f)
        except Exception as e:
            logging.error(f"Failed to parse TOML file {toml_path}: {e}")
            return

        base_ignore_dir = toml_path.parent / self.ignore_base_dir

        for section_name in self.shall_section_pass:
            section_entries = config.get(section_name, [])
            if not isinstance(section_entries, list):
                # single table fallback
                if isinstance(section_entries, dict):
                    section_entries = [section_entries]
                else:
                    continue

            if section_entries:
                self.process_section(
                    toml_path,
                    section_name,
                    section_entries,
                    base_ignore_dir,
                )

    def run(self, directories: List[str]) -> None:
        for base_dir in directories:
            base_path = Path(base_dir)
            if not base_path.is_dir():
                logging.warning(f"Not a directory, skipping: {base_path}")
                continue

            for toml_path in base_path.rglob(".dia-pull.toml"):
                logging.info(f"Processing {toml_path}")
                self.process_toml_file(toml_path)
