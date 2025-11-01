"""Configuration management for taskfile-help."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import sys
import tomllib
from typing import Any

from .discovery import TaskfileDiscovery


def _load_pyproject_config() -> dict[str, Any]:
    """Load taskfile-help configuration from pyproject.toml if it exists.

    Returns:
        Dictionary with configuration values, empty if file doesn't exist or no config found
    """
    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        return {}

    try:
        with open(pyproject_path, "rb") as f:
            data: dict[str, Any] = tomllib.load(f)
            tool_section: dict[str, Any] = data.get("tool", {})
            config: dict[str, Any] = tool_section.get("taskfile-help", {})
            return config
    except Exception:
        # Silently ignore any parsing errors
        return {}


@dataclass
class Args:
    """Parsed command-line arguments."""

    command: str
    namespace: str
    pattern: str | None
    patterns: list[str] | None
    regex: str | None
    regexes: list[str] | None
    no_color: bool
    search_dirs: list[Path] | None
    verbose: bool
    json_output: bool
    completion: str | None
    complete: str | None
    install_completion: str | None

    @staticmethod
    def _add_global_arguments(parser: argparse.ArgumentParser, list_of_paths: Callable[[str], list[Path]]) -> None:
        """Add global arguments to a parser.

        Args:
            parser: ArgumentParser to add arguments to
            list_of_paths: Function to parse colon-separated paths
        """
        parser.add_argument(
            "--no-color",
            action="store_true",
            dest="no_color",
            help="Disable colored output",
        )
        parser.add_argument(
            "--search-dirs",
            "-s",
            type=list_of_paths,
            dest="search_dirs",
            default=None,
            help="Colon-separated list of directories to search for taskfiles. "
            "Paths may be absolute or relative to current working directory. "
            "(default: current working directory)",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            dest="verbose",
            help="Show verbose output including search directories",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            dest="json_output",
            help="Output tasks in JSON format",
        )
        parser.add_argument(
            "--completion",
            type=str,
            dest="completion",
            default=None,
            metavar="SHELL",
            help="Generate completion script for specified shell (bash, zsh, fish, tcsh, ksh)",
        )
        parser.add_argument(
            "--complete",
            type=str,
            dest="complete",
            default=None,
            metavar="WORD",
            help=argparse.SUPPRESS,  # Hidden flag for shell completion callbacks
        )
        parser.add_argument(
            "--install-completion",
            type=str,
            dest="install_completion",
            default=None,
            nargs="?",
            const="auto",
            metavar="SHELL",
            help="Install completion script for specified shell (auto-detects if not specified)",
        )

    @staticmethod
    def parse_args(argv: list[str]) -> Args:
        """Parse command line arguments using argparse.

        Args:
            argv: List of command line arguments

        Returns:
            Args: Parsed arguments
        """

        def list_of_paths(arg: str) -> list[Path]:
            # Use dict.fromkeys() to remove duplicates while preserving order (keeps first occurrence)
            return list(dict.fromkeys(Path(p).resolve() for p in arg.split(":")))

        parser = argparse.ArgumentParser(
            description="Dynamic Taskfile help generator",
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            dest="command",
            help="Command to execute",
            required=True,
        )

        # Namespace command (current behavior)
        namespace_parser = subparsers.add_parser(
            "namespace",
            help="Show tasks for a specific namespace",
            description="Display tasks from a specific namespace or all namespaces",
            epilog="""
Meta-namespaces:
  main    Show tasks from the main Taskfile (default if no namespace specified)
  all     Show tasks from all Taskfiles (main + all namespaces)
  ?       List all available namespaces

Examples:
  taskfile-help namespace              # Show main Taskfile
  taskfile-help namespace main         # Show main Taskfile (explicit)
  taskfile-help namespace dev          # Show dev namespace
  taskfile-help namespace all          # Show all namespaces
  taskfile-help namespace ?            # List available namespaces
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        namespace_parser.add_argument(
            "namespace",
            nargs="?",
            default="",
            help="Namespace to show (or 'main', 'all', '?' for meta-namespaces)",
        )
        Args._add_global_arguments(namespace_parser, list_of_paths)

        # Search command (new feature)
        search_parser = subparsers.add_parser(
            "search",
            help="Search for tasks by pattern or regex",
            description="Search across namespaces, groups, and task names",
            epilog="""\nSearch filters:
  One or more search patterns can be provided as positional arguments.
  Multiple --regex options can be provided for regular expression matching.
  At least one pattern or regex is required.
  All patterns and regexes are combined with AND logic (all must match).

Search scope:
  Searches across namespace names, group names, task names, and descriptions.
  A match occurs when ALL patterns and regexes match in any combination of these fields.

Examples:
  taskfile-help search test                           # Find tasks with "test" anywhere
  taskfile-help search version bump                   # Find tasks with both "version" AND "bump"
  taskfile-help search minor version                  # Find tasks with both "minor" AND "version"
  taskfile-help search --regex "^test"                # Find tasks starting with "test"
  taskfile-help search lint --regex "fix$"            # Find "lint" tasks ending with "fix"
  taskfile-help search --regex "test" --regex "unit"  # Find tasks matching both regexes
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        search_parser.add_argument(
            "patterns",
            type=str,
            nargs="*",
            help="Search patterns (case-insensitive substring match). Multiple patterns are combined with AND logic.",
        )
        search_parser.add_argument(
            "--regex",
            type=str,
            action="append",
            dest="regexes",
            default=None,
            metavar="STR",
            help="Regular expression pattern filter (can be specified multiple times)",
        )
        Args._add_global_arguments(search_parser, list_of_paths)

        parsed = parser.parse_args(argv[1:])

        # Extract command and command-specific arguments
        command = parsed.command if parsed.command else "namespace"
        namespace = getattr(parsed, "namespace", "")
        patterns = getattr(parsed, "patterns", None)
        # For backward compatibility, keep pattern as the first pattern if patterns exist
        pattern = patterns[0] if patterns and len(patterns) > 0 else None
        regexes = getattr(parsed, "regexes", None)
        # For backward compatibility, keep regex as the first regex if regexes exist
        regex = regexes[0] if regexes and len(regexes) > 0 else None

        return Args(
            command=command,
            namespace=namespace,
            pattern=pattern,
            patterns=patterns,
            regex=regex,
            regexes=regexes,
            no_color=parsed.no_color,
            search_dirs=parsed.search_dirs,
            verbose=parsed.verbose,
            json_output=parsed.json_output,
            completion=parsed.completion,
            complete=parsed.complete,
            install_completion=parsed.install_completion,
        )


class Config:
    """Application configuration with derived values."""

    @staticmethod
    def _get_search_dirs_from_pyproject(config: dict[str, Any]) -> list[Path]:
        """Extract and resolve search directories from pyproject.toml config.

        Args:
            config: Configuration dictionary from pyproject.toml

        Returns:
            List of resolved Path objects from config
        """
        config_dirs = config["search-dirs"]
        if isinstance(config_dirs, list):
            return [Path(d).resolve() for d in config_dirs if d]
        else:
            return [Path(config_dirs).resolve()] if config_dirs else []

    @staticmethod
    def _resolve_search_dirs(
        args_search_dirs: list[Path] | None,
        pyproject_config: dict[str, Any],
    ) -> list[Path]:
        """Resolve search directories from arguments and config.

        Args:
            args_search_dirs: Search directories from command-line arguments
            pyproject_config: Configuration from pyproject.toml

        Returns:
            List of resolved search directory paths (deduplicated, preserving order)
        """
        search_dirs: list[Path]

        if args_search_dirs is not None:
            # Command-line argument takes precedence
            search_dirs = args_search_dirs[:]
        elif "search-dirs" in pyproject_config:
            # Use config from pyproject.toml
            search_dirs = Config._get_search_dirs_from_pyproject(pyproject_config)
        else:
            # Default to current working directory
            search_dirs = [Path.cwd()]

        # Handle edge case of all-empty paths
        if not search_dirs:
            search_dirs = [Path.cwd()]

        # Remove duplicates while preserving order (dict preserves insertion order in Python 3.7+)
        return list(dict.fromkeys(search_dirs))

    def __init__(self, argv: list[str]) -> None:
        """Initialize configuration from command-line arguments.

        Args:
            argv: List of command line arguments
        """
        self.args = Args.parse_args(argv)

        # Load configuration from pyproject.toml if available
        pyproject_config = _load_pyproject_config()

        # Colorize if output is a TTY and --no-color is not specified
        self.colorize = sys.stdout.isatty() and not self.args.no_color

        # Resolve taskfile search directories
        search_dirs = self._resolve_search_dirs(self.args.search_dirs, pyproject_config)

        self.discovery = TaskfileDiscovery(search_dirs)

    @property
    def namespace(self) -> str:
        """The requested namespace."""
        return self.args.namespace
