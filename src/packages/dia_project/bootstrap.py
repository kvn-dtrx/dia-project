# ---
# title: Bootstrap paths for dia-project
# ---

# ---

import os
import subprocess
from pathlib import Path

# Path relative with respect to the repository root.
DEFAULT_CONFIG_PATH_REL = "src/packages/dia_project/config.yaml"

# User override: $DIA_CONF, or ~/.config/dia.conf when unset.
DIA_CONF_ENV = "DIA_CONF"
DEFAULT_USER_CONFIG = Path.home() / ".config" / "dia.conf"


def get_project_dir() -> Path:
    caller_dir = Path(__file__).resolve().parent
    cmd = ["git", "-C", str(caller_dir), "rev-parse", "--show-toplevel"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    project_dir = Path(result.stdout.strip())
    return project_dir


PROJECT_DIR = get_project_dir()
DEFAULT_CONFIG_PATH = PROJECT_DIR / DEFAULT_CONFIG_PATH_REL

# In-repo illustration / test fixtures (not the production snippet library).
EXAMPLES_DIR = PROJECT_DIR / "examples"


def resolve_user_config_path() -> Path:
    """Return $DIA_CONF if set, else ~/.config/dia.conf."""
    raw = os.environ.get(DIA_CONF_ENV)
    if raw is not None and str(raw).strip() != "":
        return Path(str(raw).strip()).expanduser()
    return DEFAULT_USER_CONFIG
