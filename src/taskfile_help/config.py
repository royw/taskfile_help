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
    patterns: list[str] | None
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
    def _list_of_paths(arg: str) -> list[Path]:
        """Parse colon-separated paths and remove duplicates."""
        return list(dict.fromkeys(Path(p).resolve() for p in arg.split(":")))

    @staticmethod
    def _create_namespace_parser(
        subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
        list_of_paths: Callable[[str], list[Path]],
    ) -> None:
        """Create namespace command parser.

        Args:
            subparsers: Subparsers action to add the namespace parser to
            list_of_paths: Function to parse colon-separated paths
        """
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

    @staticmethod
    def _create_search_parser(
        subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
        list_of_paths: Callable[[str], list[Path]],
    ) -> None:
        """Create search command parser.

        Args:
            subparsers: Subparsers action to add the search parser to
            list_of_paths: Function to parse colon-separated paths
        """
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

    @staticmethod
    def _extract_command_values(parsed: argparse.Namespace) -> tuple[str, str, list[str] | None, list[str] | None]:
        """Extract command-specific arguments from parsed namespace.

        Args:
            parsed: Parsed argparse.Namespace containing command-line arguments

        Returns:
            Tuple of (command, namespace, patterns, regexes) where:
            - command: The subcommand name ("namespace" or "search")
            - namespace: The namespace argument (for namespace command)
            - patterns: List of all search patterns (for search command)
            - regexes: List of all regex patterns (for search command)
        """
        command = parsed.command if parsed.command else "namespace"
        namespace = getattr(parsed, "namespace", "")
        patterns = getattr(parsed, "patterns", None)
        regexes = getattr(parsed, "regexes", None)
        return command, namespace, patterns, regexes

    @staticmethod
    def parse_args(argv: list[str]) -> Args:
        """Parse command line arguments using argparse.

        Uses a two-pass approach:
        1. Parse global options from anywhere in argv
        2. Parse command-specific options with remaining args

        This allows global options to appear both before and after the subcommand.

        Args:
            argv: List of command line arguments

        Returns:
            Args: Parsed arguments
        """
        # First pass: parse global options only
        global_parser = argparse.ArgumentParser(add_help=False)
        Args._add_global_arguments(global_parser, Args._list_of_paths)
        global_args, remaining_argv = global_parser.parse_known_args(argv[1:])

        # Second pass: parse commands with remaining args
        command_parser = argparse.ArgumentParser(
            description="Dynamic Taskfile help generator",
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Add global arguments to command parser for help display
        Args._add_global_arguments(command_parser, Args._list_of_paths)

        # Create subparsers for commands
        subparsers = command_parser.add_subparsers(
            dest="command",
            help="Command to execute",
            required=True,
        )

        # Create command parsers (global arguments added for help display)
        Args._create_namespace_parser(subparsers, Args._list_of_paths)
        Args._create_search_parser(subparsers, Args._list_of_paths)

        # Parse all arguments with command parser
        command_args = command_parser.parse_args(argv[1:])

        # Extract command and command-specific arguments
        command, namespace, patterns, regexes = Args._extract_command_values(command_args)

        # Use global_args for global options (parsed from anywhere in argv)
        return Args(
            command=command,
            namespace=namespace,
            patterns=patterns,
            regexes=regexes,
            no_color=global_args.no_color,
            search_dirs=global_args.search_dirs,
            verbose=global_args.verbose,
            json_output=global_args.json_output,
            completion=global_args.completion,
            complete=global_args.complete,
            install_completion=global_args.install_completion,
            group_pattern=global_args.group_pattern,
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
    def _get_search_dirs(file_config: dict[str, Any]) -> list[Path]:
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
        return search_dirs

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
        search_dirs: list[Path] = (
            args_search_dirs[:] if args_search_dirs is not None else Config._get_search_dirs(file_config)
        )

        # Handle edge case of all-empty paths
        if not search_dirs:
            search_dirs = [Path.cwd()]

        # Remove duplicates while preserving order (dict preserves insertion order in Python 3.7+)
        return list(dict.fromkeys(search_dirs))

    @staticmethod
    def _check_no_color_env() -> bool:
        """Check environment variables for no-color setting.

        Returns:
            True if NO_COLOR or TASKFILE_HELP_NO_COLOR is set
        """
        # Check standard NO_COLOR environment variable (https://no-color.org/)
        if os.environ.get("NO_COLOR"):
            return True

        # Check taskfile-help specific environment variable
        env_no_color = os.environ.get("TASKFILE_HELP_NO_COLOR")
        return bool(env_no_color and env_no_color.lower() in ("1", "true", "yes"))

    @staticmethod
    def _get_no_color_from_config(file_config: dict[str, Any]) -> bool:
        """Get no-color setting from config file.

        Returns:
            Boolean from config file, or False if not set
        """
        return bool(file_config.get("no-color", False))

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

        # Check environment variables
        if Config._check_no_color_env():
            return True

        # Configuration file
        return Config._get_no_color_from_config(file_config)

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
