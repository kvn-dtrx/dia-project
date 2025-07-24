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
    manifest = session.general.manifest
    for directory in directories:
        base = Path(directory)
        for path in base.rglob(manifest):
            if path.is_file():
                path_parent = path.parent.resolve()
                logging.info(f"Processing manifest in:\n  {path_parent}")
                process_project(session, path_parent)
                logging.info(f"Processed manifest in:\n  {path_parent}")


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
    name = task.name
    sources_ = task.sources
    target = task.target
    combined_contents: List[str] = []
    resources = DEFAULT_RESOURCES_PATH
    sources = [resources / name / source for source in sources_]
    target = (root / target_).resolve()
    if name != "license":
        content = fill_template(
            TEMPLATE_PATH, sources, file_type=name, filename=target_
        )
    elif len(sources) == 1:
        content = from_file(*sources)
    else:
        logging.info(f"Unimplemented case.")
        return
    if content is None:
        logging.info(
            f"Cannot write:\n  Sources: {sources_}\n  Target:  {target}"
        )
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if session.ephemeral.dry_run:
        logging.info(
            f"Would write:\n  Sources: {sources_}\n  Target : {target}"
        )
    else:
        try:
            logging.debug(f"Writing target file: {target}")
            with target.open("w", encoding="utf-8") as f:
                f.write(content)
                pass
            logging.info(f"Wrote combined {name} to: {target}")
        except Exception as e:
            logging.error(f"Failed to write {target}: {e}")
