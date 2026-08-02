# ---
# title: Utility Functions for dia-project
# ---

# ---

import logging
import sys
from datetime import datetime
from pathlib import Path

import tomllib
import yaml
from box import Box
from jinja2 import Template

from .bootstrap import *


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


def from_yaml(yaml_path: Path) -> Box:
    try:
        with open(yaml_path, encoding="utf-8") as f:
            data_ = yaml.safe_load(f)
        if data_ is None:
            data_ = {}
        data = Box(data_, default_box=True)
    except Exception as e:
        logging.error(f"Failed to parse YAML file:\n  {yaml_path}\n  {e}")
        sys.exit(1)
    return data


def from_default_yaml() -> Box:
    return from_yaml(DEFAULT_CONFIG_PATH)


def from_user_yaml() -> Box | None:
    """Load $DIA_CONF / ~/.config/dia.conf when the file exists (YAML)."""
    path = resolve_user_config_path()
    if not path.is_file():
        return None
    return from_yaml(path)


def load_config() -> Box:
    """Repo default, then optional user overrides from DIA_CONF."""
    session = Box(default_box=True)
    session.merge_update(from_default_yaml())
    user = from_user_yaml()
    if user is not None:
        session.merge_update(user)
        logging.debug(f"Merged user config:\n  {resolve_user_config_path()}")
    return session


def from_file(text_path: Path) -> str | None:
    try:
        with open(text_path, encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        logging.debug(f"Skipping non-UTF-8 file:\n  {text_path}")
        return
    except OSError as e:
        logging.error(f"Failed to read file:\n  {text_path}\n  {e}")
        return
    return text


def fill_template(
    template_path: Path,
    sources: list[Path],
    file_type: str,
    filename: str,
) -> str | None:
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
    contents: list[str] = []
    for source in sources:
        if source.is_file():
            logging.debug(f"Reading source file: {source}")
            try:
                with source.open("r", encoding="utf-8") as f:
                    contents.append(f.read())
                logging.debug(f"Reading source file was successful:\n  {source}")
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
