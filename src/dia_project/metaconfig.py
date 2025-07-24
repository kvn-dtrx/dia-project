# ---
# description: Stores the required meta configurations.
# ---

# ---

# Path relative with respect to the repository root.
DEFAULT_CONFIG_PATH_REL = "src/dia_project/config.toml"
DEFAULT_RESOURCES_PATH_REL = "resources/"

# Path relative with respect to the home directory.
USER_CONFIG_PATH_REL = ".config/dia-project/config.toml"

# Path relative with respect to the resources directory.
TEMPLATE_PATH_REL = "template.j2"

# ---

import subprocess
from pathlib import Path


def get_project_dir() -> Path:
    caller_dir = Path(__file__).resolve().parent
    cmd = ["git", "-C", str(caller_dir), "rev-parse", "--show-toplevel"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    project_dir = Path(result.stdout.strip())
    return project_dir


PROJECT_DIR = get_project_dir()
DEFAULT_CONFIG_PATH = PROJECT_DIR / DEFAULT_CONFIG_PATH_REL
DEFAULT_RESOURCES_PATH = PROJECT_DIR / DEFAULT_RESOURCES_PATH_REL

HOME_DIR = Path.home()
USER_CONFIG_PATH = HOME_DIR / USER_CONFIG_PATH_REL

TEMPLATE_PATH = DEFAULT_RESOURCES_PATH / TEMPLATE_PATH_REL
