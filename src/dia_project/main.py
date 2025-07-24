#!/usr/bin/env python3

# ---
# description: Copies isolated resources specified in .dia-pull.toml.
# ---

"""
Process .dia-pull.toml files with multiple sections (gitignore, latexmkrc, flake8...).
Each section expects:
[[section]]
source = ["foo", "bar"]
target = "relative/path/to/outputfile"
"""


from dia_pull.cli import DiaPullCLI
from dia_pull.processor import DiaPullProcessor
import logging

def main():
    cli = DiaPullCLI()
    args = cli.parse_args()
    logging.basicConfig(level=logging.INFO)
    processor = DiaPullProcessor(args)
    processor.process()

if __name__ == "__main__":
    main()