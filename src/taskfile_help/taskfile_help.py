#!/usr/bin/env python3
"""
Dynamic Taskfile help generator.

Parses Taskfile YAML files and outputs organized, colored help text similar to
`task --list`, but with automatic grouping and namespace support.

File Naming Conventions:
    - Main Taskfile: Taskfile.yml or Taskfile.yaml
    - Namespace Taskfiles: Taskfile-<namespace>.yml or Taskfile-<namespace>.yaml
      Examples: Taskfile-rag.yml, Taskfile-dev.yml, Taskfile-agent.yml

Search Behavior:
    - By default, searches for taskfiles in the current working directory
    - Use --search-dirs (or -s) to search in one or more directories (first match wins)
    - Paths can be absolute (/path/to/dir) or relative (../dir, ./subdir)
    - Relative paths are resolved from the current working directory
    - Taskfiles can be located anywhere in the search path(s)

Task Organization:
    Tasks are automatically grouped using comment markers in the Taskfile:

        # === Group Name ===
        task-name:
          desc: Task description
          cmds: [...]

        task2-name:
          desc: Task2 description
          cmds: [...]

        # === Group2 Name ===

    Example groups: "Service Management", "Testing", "Build and Release"

    The output preserves the order of groups and tasks as they appear in the file.

Task Visibility:
    - Public tasks: Have a 'desc' field and no 'internal: true' flag
    - Internal tasks: Marked with 'internal: true' (excluded from help)
    - Tasks without descriptions are excluded from help output

Output Behavior:
    - Colors enabled: When output is to a terminal (TTY) and --no-color is not specified
    - Colors disabled: When output is piped, redirected, captured, or --no-color is used
    - Matches the behavior of 'task --list'
"""
# ruff: noqa: T201

from __future__ import annotations

import sys

from .config import Config
from .output import Colors, JsonOutputter, Outputter, TextOutputter
from .parser import parse_taskfile


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: List of command line arguments (defaults to sys.argv if None)

    Returns:
        int: Exit code
    """
    if argv is None:
        argv = sys.argv
    config = Config(argv)

    # Select outputter based on format
    outputter: Outputter = JsonOutputter() if config.args.json_output else TextOutputter()

    # Disable colors if output is not a TTY (piped, redirected, etc.) or JSON output
    if not config.colorize or config.args.json_output:
        Colors.disable()

    # Show verbose output if requested
    if config.args.verbose and not config.args.json_output:
        outputter.output_heading("Searching in directories:", output_fn=lambda msg: print(msg, file=sys.stderr))
        for search_dir in config.discovery.search_dirs:
            outputter.output_message(f"  {search_dir}", output_fn=lambda msg: print(msg, file=sys.stderr))
        outputter.output_message("", output_fn=lambda msg: print(msg, file=sys.stderr))

    namespace = config.namespace

    # Special case: 'all' namespace shows all Taskfiles
    if namespace == "all":
        # Collect all tasks
        taskfiles: list[tuple[str, list[tuple[str, str, str]]]] = []

        main_taskfile = config.discovery.find_main_taskfile()
        if main_taskfile:
            tasks = parse_taskfile(main_taskfile, "", outputter)
            taskfiles.append(("", tasks))

        for ns, taskfile_path in config.discovery.get_all_namespace_taskfiles():
            tasks = parse_taskfile(taskfile_path, ns, outputter)
            taskfiles.append((ns, tasks))

        outputter.output_all(taskfiles)
        return 0

    # Find the appropriate Taskfile
    if not namespace or namespace == "main":
        taskfile = config.discovery.find_main_taskfile()
        namespace = ""  # Use empty namespace for display
    else:
        taskfile = config.discovery.find_namespace_taskfile(namespace)

    if not taskfile:
        possible_paths = config.discovery.get_possible_paths(namespace)
        outputter.output_error(f"No Taskfile found for namespace '{namespace}'")
        outputter.output_warning(f"Tried: {', '.join(str(p) for p in possible_paths)}")
        return 1

    # Parse and display tasks
    tasks = parse_taskfile(taskfile, namespace, outputter)
    outputter.output_single(namespace, tasks)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
