# ---
# description: Provides some required utility functions.
# ---

# ---

import tomllib
import logging
import sys
from box import Box
from datetime import datetime
from pathlib import Path
from jinja2 import Template
from typing import List
from typing import Optional
from .metaconfig import *


def from_toml(toml_path: Path) -> Box:
    try:
        with open(toml_path, "rb") as f:
            data_ = tomllib.load(f)
        data = Box(data_, default_box=True)
    except Exception as e:
        logging.error(f"Failed to parse TOML file:\n  {toml_path}\n  {e}")
        sys.exit(1)
    return data


def from_default_toml() -> Box:
    data = from_toml(DEFAULT_CONFIG_PATH)
    return data


def from_file(text_path: Path) -> Optional[str]:
    try:
        with open(text_path, "r") as f:
            text = f.read()
        # data = Box(text_, default_box=True)
    except Exception as e:
        logging.error(f"Failed to read file:\n  {text_path}\n  {e}")
        return
    return text


def fill_template(
    template_path: Path,
    sources: List[Path],
    file_type: str,
    filename: str,
) -> Optional[str]:
    logging.debug(f"Reading template file: {template_path}")
    try:
        with template_path.open("r", encoding="utf-8") as f:
            template_text = f.read()
        logging.debug(f"Reading template file was successful: {template_path}")
    except Exception as e:
        logging.error(f"Failed to read {template_path}: {e}")
        return
    template = Template(template_text)
    now_iso = datetime.now().replace(microsecond=0).isoformat()
    contents: List[str] = []
    for source in sources:
        if source.is_file():
            logging.debug(f"Reading source file: {source}")
            try:
                with source.open("r", encoding="utf-8") as f:
                    contents.append(f.read())
                logging.debug(
                    f"Reading source file was successful:\n  {source}"
                )
            except Exception as e:
                logging.error(f"Failed to read {source}: {e}")
        else:
            logging.error(f"Source file not found:\n  {source}")
            return

    filled_template = template.render(
        type=file_type,
        filename=filename,
        contents=contents,
        date=now_iso,
    )
    filled_template = filled_template + "\n"
    return filled_template
