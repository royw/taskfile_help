import argparse
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

    show_all: bool
    namespace: str
    no_color: bool
    search_dirs: list[Path]
    verbose: bool
    json_output: bool

    @staticmethod
    def parse_args(argv: list[str]) -> "Args":
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
        parser.add_argument(
            "namespace",
            nargs="?",
            default="",
            help="Namespace to show help for (e.g., 'rag', 'dev', 'main')",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            dest="show_all",
            help="Show help for all taskfiles",
        )
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
            default=[Path.cwd()],
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

        parsed = parser.parse_args(argv[1:])
        return Args(
            show_all=parsed.show_all,
            namespace=parsed.namespace,
            no_color=parsed.no_color,
            search_dirs=parsed.search_dirs,
            verbose=parsed.verbose,
            json_output=parsed.json_output,
        )


class Config:
    """Application configuration with derived values."""

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

        # Parse taskfile search directories
        if self.args.search_dirs:
            # Command-line argument takes precedence
            # Split colon-separated paths and convert to absolute Path objects
            search_dirs = self.args.search_dirs[:]
        elif "search-dirs" in pyproject_config:
            # Use config from pyproject.toml
            config_dirs = pyproject_config["search-dirs"]
            if isinstance(config_dirs, list):
                search_dirs = [Path(d).resolve() for d in config_dirs if d]
            else:
                search_dirs = [Path(config_dirs).resolve()] if config_dirs else []
        else:
            # Default to current working directory
            search_dirs = [Path.cwd()]

        # Handle edge case of all-empty paths
        if not search_dirs:
            search_dirs = [Path.cwd()]

        # Remove duplicates while preserving order (dict preserves insertion order in Python 3.7+)
        search_dirs = list(dict.fromkeys(search_dirs))

        self.discovery = TaskfileDiscovery(search_dirs)

    @property
    def show_all(self) -> bool:
        """Whether to show all taskfiles."""
        return self.args.show_all

    @property
    def namespace(self) -> str:
        """The requested namespace."""
        return self.args.namespace
