# ---
# description: CLI argparsing logic
# ---

# ---

import argparse
import logging
from box import Box
from typing import Callable


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copies isolated resources specified in dia-project's manifests"
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=["."],
        help="Directories to recursively search for manifests. Defaults to current directory.",
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
    parser.add_argument(
        "-w",
        "--whitelist",
        nargs="+",
        metavar="SECTION",
        help="Whitelists these sections (mutually exclusive with --blacklist).",
    )
    parser.add_argument(
        "-b",
        "--blacklist",
        nargs="+",
        metavar="SECTION",
        help="Blacklists these sections (mutually exclusive with --whitelist).",
    )
    parser.add_argument(
        "-r",
        "--resources",
        nargs="+",
        metavar="PATHS",
        help="Comma-separated list of resource file paths (relative or absolute).",
    )
    return parser


def from_args() -> Box:
    config = {}
    config["general"] = {}
    config["ephemeral"] = {}

    parser = get_parser()
    parsed_args = parser.parse_args()

    if parsed_args.whitelist and parsed_args.blacklist:
        parser.error("Cannot use both --whitelist and --blacklist.")

    if parsed_args.resources:
        additional_resources = [
            p.strip() for p in parsed_args.resources.split(",")
        ]
        config["general"]["additional_resources"] = additional_resources

    config["ephemeral"]["directories"] = parsed_args.directories

    section_filter: Callable[[str], bool]
    if parsed_args.whitelist:
        section_filter = lambda section: section in parsed_args.whitelist
    elif parsed_args.blacklist:
        section_filter = lambda section: section not in parsed_args.blacklist
    else:
        section_filter = lambda _: True
    config["ephemeral"]["section_filter"] = section_filter

    if parsed_args.verbose:
        config["general"]["log_level"] = logging.DEBUG

    config["ephemeral"]["dry_run"] = parsed_args.dry_run
    config = Box(config, default_box=True)

    return config
