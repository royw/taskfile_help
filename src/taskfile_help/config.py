"""Configuration management for taskfile-help."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
import os
from pathlib import Path
import sys
import tomllib
from typing import Any, Protocol

import yaml

from .discovery import TaskfileDiscovery


class ConfigFile(Protocol):
    """Protocol for configuration file readers.

    Implementations must provide a method to load configuration data
    from a specific file format.
    """

    def load_config(self) -> dict[str, Any]:
        """Load configuration from the file.

        Returns:
            Dictionary with configuration values, empty if file doesn't exist or parsing fails
        """
        ...


class PyProjectConfigFile:
    """Configuration file reader for pyproject.toml files."""

    def __init__(self, file_path: Path) -> None:
        """Initialize with path to pyproject.toml file.

        Args:
            file_path: Path to the pyproject.toml file
        """
        self.file_path = file_path

    def load_config(self) -> dict[str, Any]:
        """Load taskfile-help configuration from pyproject.toml.

        Returns:
            Dictionary with configuration values from [tool.taskfile-help] section,
            empty if file doesn't exist or no config found
        """
        if not self.file_path.exists():
            return {}

        try:
            with open(self.file_path, "rb") as f:
                data: dict[str, Any] = tomllib.load(f)
                tool_section: dict[str, Any] = data.get("tool", {})
                config: dict[str, Any] = tool_section.get("taskfile-help", {})
                return config
        except Exception:
            # Silently ignore any parsing errors
            return {}


class TaskfileHelpConfigFile:
    """Configuration file reader for taskfile_help.yml files."""

    def __init__(self, file_path: Path) -> None:
        """Initialize with path to taskfile_help.yml file.

        Args:
            file_path: Path to the taskfile_help.yml file
        """
        self.file_path = file_path

    def load_config(self) -> dict[str, Any]:
        """Load taskfile-help configuration from taskfile_help.yml.

        Returns:
            Dictionary with configuration values,
            empty if file doesn't exist or parsing fails
        """
        if not self.file_path.exists():
            return {}

        try:
            with open(self.file_path, encoding="utf-8") as f:
                data: dict[str, Any] = yaml.safe_load(f) or {}
                # The YAML file contains the config directly at the root level
                return data
        except Exception:
            # Silently ignore any parsing errors
            return {}


def get_config_file(config_file_names: list[str] | None = None) -> ConfigFile | None:
    """Factory function to get the appropriate ConfigFile implementation.

    Searches the current directory for config files in the order specified.
    Returns the first one found.

    Args:
        config_file_names: List of config file names to search for in order.
                          Defaults to ["taskfile_help.yml", "pyproject.toml"]

    Returns:
        ConfigFile implementation for the first found config file, or None if none found
    """
    # Mapping of config filenames to their implementation classes
    config_class_map: dict[str, type[PyProjectConfigFile] | type[TaskfileHelpConfigFile]] = {
        "pyproject.toml": PyProjectConfigFile,
        "taskfile_help.yml": TaskfileHelpConfigFile,
    }

    if config_file_names is None:
        config_file_names = ["taskfile_help.yml", "pyproject.toml"]

    cwd = Path.cwd()

    for config_name in config_file_names:
        config_path = cwd / config_name
        if config_path.exists() and config_name in config_class_map:
            config_class = config_class_map[config_name]
            return config_class(config_path)

    return None


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
    group_pattern: str | None

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
        parser.add_argument(
            "--group-pattern",
            type=str,
            dest="group_pattern",
            default=None,
            metavar="PATTERN",
            help='Regular expression pattern for group markers (default: r"\\s*#\\s*===\\s*(.+?)\\s*===")',
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
            group_pattern=parsed.group_pattern,
        )


class Config:
    """Application configuration with derived values."""

    @staticmethod
    def _get_search_dirs_from_config(config: dict[str, Any]) -> list[Path]:
        """Extract and resolve search directories from config file.

        Args:
            config: Configuration dictionary from config file

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
        file_config: dict[str, Any],
    ) -> list[Path]:
        """Resolve search directories from arguments, environment, and config.

        Priority order:
        1. Command-line argument (--search-dirs)
        2. Environment variable (TASKFILE_HELP_SEARCH_DIRS)
        3. Configuration file (taskfile_help.yml or pyproject.toml)
        4. Default (current working directory)

        Args:
            args_search_dirs: Search directories from command-line arguments
            file_config: Configuration from config file

        Returns:
            List of resolved search directory paths (deduplicated, preserving order)
        """
        search_dirs: list[Path]

        if args_search_dirs is not None:
            # Command-line argument takes precedence
            search_dirs = args_search_dirs[:]
        else:
            # Check environment variable
            env_search_dirs = os.environ.get("TASKFILE_HELP_SEARCH_DIRS")
            if env_search_dirs:
                # Parse colon-separated paths from environment variable
                search_dirs = [Path(p).resolve() for p in env_search_dirs.split(":") if p]
            elif "search-dirs" in file_config:
                # Use config from config file
                search_dirs = Config._get_search_dirs_from_config(file_config)
            else:
                # Default to current working directory
                search_dirs = [Path.cwd()]

        # Handle edge case of all-empty paths
        if not search_dirs:
            search_dirs = [Path.cwd()]

        # Remove duplicates while preserving order (dict preserves insertion order in Python 3.7+)
        return list(dict.fromkeys(search_dirs))

    @staticmethod
    def _resolve_no_color(args_no_color: bool, file_config: dict[str, Any]) -> bool:
        """Resolve no-color setting from arguments, environment, and config.

        Priority order:
        1. Command-line argument (--no-color)
        2. Environment variable (NO_COLOR or TASKFILE_HELP_NO_COLOR)
        3. Configuration file (taskfile_help.yml or pyproject.toml)
        4. Default (False)

        Args:
            args_no_color: No-color flag from command-line arguments
            file_config: Configuration from config file

        Returns:
            Boolean indicating whether to disable colors
        """
        # Command-line argument takes precedence
        if args_no_color:
            return True

        # Check standard NO_COLOR environment variable (https://no-color.org/)
        if os.environ.get("NO_COLOR"):
            return True

        # Check taskfile-help specific environment variable
        env_no_color = os.environ.get("TASKFILE_HELP_NO_COLOR")
        if env_no_color and env_no_color.lower() in ("1", "true", "yes"):
            return True

        # Configuration file
        if "no-color" in file_config:
            return bool(file_config["no-color"])

        # Default
        return False

    @staticmethod
    def _resolve_group_pattern(
        args_group_pattern: str | None,
        file_config: dict[str, Any],
    ) -> str:
        """Resolve group pattern from arguments, environment, and config.

        Priority order:
        1. Command-line argument (--group-pattern)
        2. Environment variable (TASKFILE_HELP_GROUP_PATTERN)
        3. Configuration file (taskfile_help.yml or pyproject.toml)
        4. Default pattern

        Args:
            args_group_pattern: Group pattern from command-line arguments
            file_config: Configuration from config file

        Returns:
            Group pattern string
        """
        # Default pattern
        default_pattern = r"\s*#\s*===\s*(.+?)\s*==="

        # Command-line argument takes precedence
        if args_group_pattern is not None:
            return args_group_pattern

        # Environment variable is next
        env_pattern = os.environ.get("TASKFILE_HELP_GROUP_PATTERN")
        if env_pattern is not None:
            return env_pattern

        # Configuration file
        if "group-pattern" in file_config:
            pattern: str = file_config["group-pattern"]
            return pattern

        # Default
        return default_pattern

    def __init__(self, argv: list[str]) -> None:
        """Initialize configuration from command-line arguments.

        Args:
            argv: List of command line arguments
        """
        self.args = Args.parse_args(argv)

        # Load configuration from config file if available
        config_file = get_config_file()
        file_config = config_file.load_config() if config_file else {}

        # Resolve no-color setting
        no_color = self._resolve_no_color(self.args.no_color, file_config)

        # Colorize if output is a TTY and no-color is not set
        self.colorize = sys.stdout.isatty() and not no_color

        # Resolve taskfile search directories
        search_dirs = self._resolve_search_dirs(self.args.search_dirs, file_config)

        self.discovery = TaskfileDiscovery(search_dirs)

        # Resolve group pattern
        self.group_pattern = self._resolve_group_pattern(self.args.group_pattern, file_config)

    @property
    def namespace(self) -> str:
        """The requested namespace."""
        return self.args.namespace
