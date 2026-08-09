# ---
# description: >-
#   Parses CLI arguments for dia-project
# ---

# ---

import argparse
import logging
from pathlib import Path

from box import Box


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Embeds resource snippets into files at "
            "configurable <marker>:begin / <marker>:end markers."
        )
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=["."],
        help=(
            "Directories (or files) to scan for markers. "
            "Defaults to the current directory."
        ),
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Shows what would be done without writing files.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enables verbose (DEBUG) logging.",
    )
    return parser


def from_args() -> Box:
    config: dict = {"general": {}, "ephemeral": {}}

    parser = get_parser()
    parsed_args = parser.parse_args()

    config["ephemeral"]["directories"] = [
        Path(directory) for directory in parsed_args.directories
    ]
    config["ephemeral"]["dry_run"] = parsed_args.dry_run

    if parsed_args.verbose:
        config["general"]["log_level"] = logging.DEBUG
        logging.getLogger().setLevel(logging.DEBUG)

    return Box(config, default_box=True)
