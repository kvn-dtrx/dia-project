# ---
# title: dia-project initialisation on execution
# ---

# ---

import logging
import os
import sys

from .arg_parsing import from_args
from .processing import IntegrityError, process
from .utils import load_config

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

if os.geteuid() == 0:
    logging.critical("Please run with user and not root privileges!")
    sys.exit(1)


def main() -> int:
    session = load_config()
    updates = from_args()
    session.merge_update(updates)
    try:
        errors = process(session)
    except IntegrityError as e:
        logging.error(f"Invalid configuration:\n  {e}")
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
