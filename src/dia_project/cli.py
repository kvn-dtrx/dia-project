# ---
# description:
# ---

# ---

import argparse
import logging
from typing import Callable, List, Optional
from dia_project import DiaPullProcessor


class DiaPullCLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="Copies isolated resources specified in .dia-pull.toml."
        )
        self.parser.add_argument(
            "dirs",
            nargs="*",
            default=["."],
            help="Directories to recursively search for .dia-pull.toml files. Defaults to current directory.",
        )
        self.parser.add_argument(
            "-n",
            "--dry-run",
            action="store_true",
            help="Shows what would be done without writing files.",
        )
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enables verbose (DEBUG) logging.",
        )
        self.parser.add_argument(
            "--whitelist",
            nargs="+",
            metavar="SECTION",
            help="Whitelists these sections (mutually exclusive with --blacklist).",
        )
        self.parser.add_argument(
            "--excl-sections",
            nargs="+",
            metavar="SECTION",
            help="Blacklists these sections (mutually exclusive with --whitelist).",
        )

    def run(self, args: Optional[List[str]] = None) -> None:
        parsed_args = self.parser.parse_args(args)

        if parsed_args.incl_sections and parsed_args.excl_sections:
            self.parser.error("Cannot use both --incl-sections and --excl-sections.")

        shall_section_pass: Callable[[str], bool]
        if parsed_args.incl_sections:
            shall_section_pass = lambda section: section in parsed_args.incl_sections
        elif parsed_args.excl_sections:
            shall_section_pass = (
                lambda section: section not in parsed_args.excl_sections
            )
        else:
            shall_section_pass = lambda _: True

        log_level = logging.DEBUG if parsed_args.verbose else logging.INFO

        processor = DiaPullProcessor(
            ignore_base_dir=parsed_args.ignore_base_dir,
            shall_section_pass=shall_section_pass,
            log_level=log_level,
        )
        processor.run(parsed_args.dirs)
