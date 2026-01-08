# ---
# title: dia-project initialisation on execution
# ---

"""
Process .dia-pull.toml files with multiple sections (gitignore, latexmkrc, flake8...).
Each section expects:
[section]
source = ["foo", "bar"]
target = "relative/path/to/outputfile"
"""

# ---

import logging
import os
import sys

from box import Box

from .arg_parsing import from_args
from .processing import process
from .utils import from_default_yaml

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

if os.geteuid() == 0:
    logging.critical("Please run with user and not root privileges!")
    sys.exit(1)


def main() -> int:
    session = Box(default_box=True)
    # try:
    # updates = from_default_toml()
    updates = from_default_yaml()
    session.merge_update(updates)
    updates = from_args()
    session.merge_update(updates)
    process(session)
    # # except Exception as e:
    # #     print(f"Error:\n  {e}", file=sys.stderr)
    # #     return 1
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
