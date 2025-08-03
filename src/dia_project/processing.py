# ---
# description: Processes the configurations.
# ---

# ---

import logging
from typing import List
from typing import Optional
from pathlib import Path
from box import Box
from box import BoxList
from .metaconfig import *
from .utils import *


CMT = {
    "flake8": ("# ", ""),
    "gitignore": ("# ", ""),
    "latexmkrc": ("# ", ""),
    "license": ("<!-- ", " -->"),
    "makefile": ("# ", ""),
    "markdownlint": ("# ", ""),
    "prettierrc": ("// ", ""),
    "pylintrc": ("# ", ""),
    "readme": ("<!-- ", " -->"),
}


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
    for k_task, v_tasks in tasks.items():
        task_passed = session.ephemeral.section_filter(k_task)
        if task_passed:
            if isinstance(v_tasks, Box):
                v_tasks = BoxList([v_tasks])
            for v_task in v_tasks:
                process_project_task(session, root, k_task, v_task)


def process_project_task(
    session: Box, root: Path, key: str, task: Box
) -> None:
    name = key
    sources_ = task.sources
    if not sources_:
        logging.info(f"No sources specified for: {name}")
        return
    target_ = task.target
    if "as_symlink" in task:
        as_symlink = task.as_symlink
    else:
        as_symlink = False
    resources = DEFAULT_RESOURCES_PATH
    sources = [resources / name / source for source in sources_]
    target = (root / target_).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not as_symlink:
        contents: List[str] = []
        for source in sources:
            content = from_file(source)
            if not content is None:
                contents.append(content)
            else:
                logging.info(
                    f"Cannot write:\n  Sources: {sources_}\n  Target:  {target}"
                )
                return
        cmtbeg, cmtend = CMT[name]
        separator = f"\n{cmtbeg}---{cmtend}\n\n"
        content = separator.join(contents)
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
    else:
        if len(sources) > 1:
            logging.info(f"Proper list of files cannot be written: {name}")
            return
        else:
            source = sources[0]
            print(target)
            if target.exists() or target.is_symlink():
                target.unlink()
            target.symlink_to(source)
