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

from .completion import (
    generate_bash_completion,
    generate_fish_completion,
    generate_ksh_completion,
    generate_tcsh_completion,
    generate_zsh_completion,
    get_completions,
    install_completion,
)
from .config import Config
from .output import Colors, JsonOutputter, Outputter, TextOutputter
from .parser import parse_taskfile
from .search import search_taskfiles


def _show_verbose_output(config: Config, outputter: Outputter) -> None:
    """Display verbose output showing search directories.

    Args:
        config: Configuration object containing args and discovery settings
        outputter: Outputter instance for formatted output
    """
    if config.args.verbose and not config.args.json_output:
        outputter.output_heading("Searching in directories:", output_fn=lambda msg: print(msg, file=sys.stderr))
        for search_dir in config.discovery.search_dirs:
            outputter.output_message(f"  {search_dir}", output_fn=lambda msg: print(msg, file=sys.stderr))
        outputter.output_message("", output_fn=lambda msg: print(msg, file=sys.stderr))


def _show_all_tasks(config: Config, outputter: Outputter) -> None:
    """Display tasks from all taskfiles (main and all namespaces).

    Collects tasks from the main taskfile and all namespace taskfiles,
    then outputs them in a consolidated format.

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output
    """
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


def _show_available_namespaces(config: Config, outputter: Outputter) -> None:
    # Suggest available namespaces
    available_namespaces = config.discovery.get_all_namespace_taskfiles()
    if available_namespaces:
        namespace_names = [ns for ns, _ in available_namespaces]
        outputter.output_message(f"\nAvailable namespaces: {', '.join(namespace_names)}")


def _show_namespace_not_found(config: Config, outputter: Outputter, namespace: str) -> None:
    """Display error message when taskfile not found and suggest alternatives.

    Shows which paths were tried and lists available namespaces to help
    the user find the correct namespace.

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output
        namespace: The namespace that was not found
    """
    possible_paths = config.discovery.get_possible_paths(namespace)
    outputter.output_error(f"No Taskfile found for namespace '{namespace}'")
    outputter.output_warning(f"Tried: {', '.join(str(p) for p in possible_paths)}")

    _show_available_namespaces(config, outputter)


def _handle_completion(config: Config) -> int | None:
    """Handle completion-related operations.

    Processes completion script generation, completion helper callbacks,
    and completion installation requests.

    Args:
        config: Configuration object containing args and settings

    Returns:
        int: Exit code if completion was handled, None otherwise
    """
    # Handle completion script generation
    if config.args.completion:
        generators = {
            "bash": generate_bash_completion,
            "zsh": generate_zsh_completion,
            "fish": generate_fish_completion,
            "tcsh": generate_tcsh_completion,
            "csh": generate_tcsh_completion,  # csh uses tcsh completion
            "ksh": generate_ksh_completion,
        }

        shell = config.args.completion.lower()
        if shell in generators:
            print(generators[shell]())
            return 0
        print(f"Error: Unknown shell '{config.args.completion}'", file=sys.stderr)
        print("Supported shells: bash, zsh, fish, tcsh, csh, ksh", file=sys.stderr)
        return 1

    # Handle completion helper (for shell callbacks)
    if config.args.complete is not None:
        completions = get_completions(config.args.complete, config.discovery.search_dirs)
        print("\n".join(completions))
        return 0

    # Handle completion installation
    if config.args.install_completion is not None:
        install_shell: str | None = None if config.args.install_completion == "auto" else config.args.install_completion
        success, message = install_completion(install_shell)
        print(message)
        return 0 if success else 1

    return None


def _handle_namespace_command(config: Config, outputter: Outputter) -> int:
    """Handle the namespace command (current behavior).

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output

    Returns:
        int: Exit code
    """
    namespace = config.namespace

    # Special case: 'all' namespace shows all Taskfiles
    if namespace == "all":
        _show_all_tasks(config, outputter)
        return 0

    # Find the appropriate Taskfile
    if not namespace or namespace == "main":
        taskfile = config.discovery.find_main_taskfile()
        namespace = ""  # Use empty namespace for display
    else:
        taskfile = config.discovery.find_namespace_taskfile(namespace)

    if not taskfile:
        if namespace == "?":
            _show_available_namespaces(config, outputter)
            return 0
        else:
            _show_namespace_not_found(config, outputter, namespace)
            return 1

    # Parse and display tasks
    tasks = parse_taskfile(taskfile, namespace, outputter)
    outputter.output_single(namespace, tasks)
    return 0


def _handle_search_command(config: Config, outputter: Outputter) -> int:
    """Handle the search command.

    Args:
        config: Configuration object containing search filters
        outputter: Outputter instance for formatted output

    Returns:
        int: Exit code
    """
    # Validate that at least one filter is provided
    if not config.args.pattern and not config.args.regex:
        outputter.output_error("At least one search filter (--pattern or --regex) is required")
        return 1

    # Collect all taskfiles (main + all namespaces)
    taskfiles: list[tuple[str, list[tuple[str, str, str]]]] = []

    main_taskfile = config.discovery.find_main_taskfile()
    if main_taskfile:
        tasks = parse_taskfile(main_taskfile, "", outputter)
        taskfiles.append(("", tasks))

    for ns, taskfile_path in config.discovery.get_all_namespace_taskfiles():
        tasks = parse_taskfile(taskfile_path, ns, outputter)
        taskfiles.append((ns, tasks))

    # Search across all taskfiles
    results = search_taskfiles(
        taskfiles,
        pattern=config.args.pattern,
        regex=config.args.regex,
    )

    # Output results
    outputter.output_search_results(results)
    return 0


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

    # Handle completion-related operations
    completion_result = _handle_completion(config)
    if completion_result is not None:
        return completion_result

    # Select outputter based on format
    outputter: Outputter = JsonOutputter() if config.args.json_output else TextOutputter()

    # Disable colors if output is not a TTY (piped, redirected, etc.) or JSON output
    if not config.colorize or config.args.json_output:
        Colors.disable()

    # Show verbose output if requested
    _show_verbose_output(config, outputter)

    # Route to appropriate command handler
    if config.args.command == "search":
        return _handle_search_command(config, outputter)
    else:
        # Default to namespace command (includes backward compatibility)
        return _handle_namespace_command(config, outputter)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
