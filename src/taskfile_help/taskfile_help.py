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

from pathlib import Path
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
from .output import Colors, Outputter, create_outputter
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


def _show_all_tasks(config: Config, outputter: Outputter) -> int:
    """Display tasks from all taskfiles (main and all namespaces).

    Collects tasks from the main taskfile and all namespace taskfiles,
    then outputs them together.

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output

    Returns:
        int: Exit code (always 0)
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
    return 0


def _show_available_namespaces(config: Config, outputter: Outputter) -> int:
    """Show available namespaces.

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output

    Returns:
        int: Exit code (always 0)
    """
    # Suggest available namespaces
    available_namespaces = config.discovery.get_all_namespace_taskfiles()
    if available_namespaces:
        namespace_list = ", ".join(ns for ns, _ in available_namespaces)
        outputter.output_message(f"\nAvailable namespaces: {namespace_list}")
    return 0


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


def _handle_completion_script_generation(shell: str) -> int:
    """Generate completion script for the specified shell.

    Args:
        shell: Shell name (bash, zsh, fish, tcsh, csh, ksh)

    Returns:
        Exit code (0 for success, 1 for unknown shell)
    """
    generators = {
        "bash": generate_bash_completion,
        "zsh": generate_zsh_completion,
        "fish": generate_fish_completion,
        "tcsh": generate_tcsh_completion,
        "csh": generate_tcsh_completion,  # csh uses tcsh completion
        "ksh": generate_ksh_completion,
    }

    shell_lower = shell.lower()
    if shell_lower in generators:
        print(generators[shell_lower]())
        return 0

    print(f"Error: Unknown shell '{shell}'", file=sys.stderr)
    print("Supported shells: bash, zsh, fish, tcsh, csh, ksh", file=sys.stderr)
    return 1


def _handle_completion_helper(word: str, search_dirs: list[Path]) -> int:
    """Handle completion helper for shell callbacks.

    Args:
        word: Partial word to complete
        search_dirs: Directories to search for Taskfiles

    Returns:
        Exit code (always 0)
    """
    completions = get_completions(word, search_dirs)
    print("\n".join(completions))
    return 0


def _handle_completion_installation(install_arg: str) -> int:
    """Handle completion installation.

    Args:
        install_arg: Shell name or "auto" for auto-detection

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    install_shell: str | None = None if install_arg == "auto" else install_arg
    success, message = install_completion(install_shell)
    print(message)
    return 0 if success else 1


def _handle_completion(config: Config) -> int | None:
    """Handle completion-related operations.

    Dispatches to specific handlers for completion script generation,
    completion helper callbacks, and completion installation.

    Args:
        config: Configuration object containing args and settings

    Returns:
        int: Exit code if completion was handled, None otherwise
    """
    if config.args.completion:
        return _handle_completion_script_generation(config.args.completion)

    if config.args.complete is not None:
        return _handle_completion_helper(config.args.complete, config.discovery.search_dirs)

    if config.args.install_completion is not None:
        return _handle_completion_installation(config.args.install_completion)

    return None


def _show_main_or_namespace(config: Config, outputter: Outputter, namespace: str) -> int:
    """Show tasks for main taskfile or a specific namespace.

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output
        namespace: The namespace to show tasks for ("main", "", or actual namespace)

    Returns:
        int: Exit code
    """
    # Find the appropriate Taskfile
    if not namespace or namespace == "main":
        taskfile = config.discovery.find_main_taskfile()
        display_namespace = ""  # Use empty namespace for display
    else:
        taskfile = config.discovery.find_namespace_taskfile(namespace)
        display_namespace = namespace

    if not taskfile:
        _show_namespace_not_found(config, outputter, namespace)
        return 1

    tasks = parse_taskfile(taskfile, display_namespace, outputter)
    outputter.output_single(display_namespace, tasks)
    return 0


def _handle_namespace_command(config: Config, outputter: Outputter) -> int:
    """Handle the namespace command (current behavior).

    Args:
        config: Configuration object containing discovery settings
        outputter: Outputter instance for formatted output

    Returns:
        int: Exit code
    """
    namespace = config.namespace

    # Handle special namespaces
    if namespace == "all":
        return _show_all_tasks(config, outputter)

    if namespace == "?":
        return _show_available_namespaces(config, outputter)

    # Handle main, empty, or specific namespace
    return _show_main_or_namespace(config, outputter, namespace)


def _handle_search_command(config: Config, outputter: Outputter) -> int:
    """Handle the search command.

    Args:
        config: Configuration object containing search filters
        outputter: Outputter instance for formatted output

    Returns:
        int: Exit code
    """
    # Validate that at least one filter is provided
    # Check if patterns list is empty or None, and regexes is empty or None
    has_patterns = config.args.patterns and len(config.args.patterns) > 0
    has_regexes = config.args.regexes and len(config.args.regexes) > 0

    if not has_patterns and not has_regexes:
        outputter.output_error("At least one search filter (pattern or --regex) is required")
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
    # Pass None instead of empty list for cleaner handling
    patterns = config.args.patterns if has_patterns else None
    regexes = config.args.regexes if has_regexes else None

    results = search_taskfiles(
        taskfiles,
        patterns=patterns,
        regexes=regexes,
    )

    # Output results
    outputter.output_search_results(results)
    return 0


def _handle_command(config: Config, outputter: Outputter) -> int:
    command_handler = {
        "namespace": _handle_namespace_command,
        "search": _handle_search_command,
    }
    if config.args.command not in command_handler:
        outputter.output_error(f"Invalid command '{config.args.command}'")
        return 1
    return command_handler[config.args.command](config, outputter)


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: List of command line arguments (defaults to sys.argv if None)

    Returns:
        int: Exit code
    """
    config = Config(argv or sys.argv)

    # Handle completion-related operations
    completion_result = _handle_completion(config)
    if completion_result is not None:
        return completion_result

    # Select outputter based on format
    outputter: Outputter = create_outputter(config)

    # Disable colors if output is not a TTY (piped, redirected, etc.) or JSON output
    if not config.colorize or config.args.json_output:
        Colors.disable()

    # Show verbose output if requested
    _show_verbose_output(config, outputter)

    # Route to appropriate command handler
    return _handle_command(config, outputter)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
