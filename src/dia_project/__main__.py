# ---
# description: Copies isolated resources specified in .dia-pull.toml.
# ---

"""
Process .dia-pull.toml files with multiple sections (gitignore, latexmkrc, flake8...).
Each section expects:
[section]
source = ["foo", "bar"]
target = "relative/path/to/outputfile"
"""

# ---

import sys
import logging
from .utils import from_default_toml
from .arg_parsing import from_args
from .processing import process
from box import Box
import os


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

if os.geteuid() == 0:
    logging.critical("Please run with user and not root privileges!")
    sys.exit(1)


def main() -> int:
    session = Box(default_box=True)
    # try:
    updates = from_default_toml()
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
