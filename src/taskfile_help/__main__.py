#!/usr/bin/env python3
"""Entry point for running taskfile_help as a module with python -m taskfile_help."""

import sys

from taskfile_help.taskfile_help import main


if __name__ == "__main__":
    sys.exit(main(sys.argv))
