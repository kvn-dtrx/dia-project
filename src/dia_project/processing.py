# ---
# description: Processes the configurations.
# ---

# ---

import logging
from typing import List
from typing import Optional
from pathlib import Path
from box import Box
from .metaconfig import *
from .utils import *


def get_resource(directories: List[Path], name: str) -> Optional[Path]:
    for directory in directories:
        for path in directory.rglob(name):
            if path.is_file():
                return path


def process(session: Box) -> None:
    directories: List[Path] = session.ephemeral.directories
    manifest: str = session.general.manifest
    for directory in directories:
        base = Path(directory)
        for path in base.rglob(manifest):
            if path.is_file():
                process_project(session, path.parent)


def process_project(session: Box, root: Path) -> None:
    manifest_file = session.general.manifest
    manifest_path = root / manifest_file
    tasks = from_toml(manifest_path)
    for k_task, v_task in tasks.items():
        task_passed = session.ephemeral.section_filter(k_task)
        if task_passed:
            process_project_task(session, root, k_task, v_task)


def process_project_task(
    session: Box, root: Path, key: str, task: Box
) -> None:
    sources = task.sources
    target = task.target
    combined_contents: List[str] = []
    resources = DEFAULT_RESOURCES_PATH
    sources = [resources / key / source for source in sources]
    filled_template = fill_template(
        TEMPLATE_PATH, sources, file_type=key, filename=target
    )
    target_path = (root / target).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    logging.debug(f"Writing target file: {target_path}")
    print(filled_template)
    try:
        with target_path.open("w", encoding="utf-8") as f:
            f.write(filled_template)
            pass
        logging.info(f"Wrote combined {key} to: {target_path}")
    except Exception as e:
        logging.error(f"Failed to write {target_path}: {e}")
    return
