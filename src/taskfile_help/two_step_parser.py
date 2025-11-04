"""Two-step argument parser for flexible global option positioning.

This module provides a reusable ArgumentParser wrapper that allows global options
to be placed before or after subcommands, using a two-pass parsing approach.

Example:
    >>> parser = TwoStepParser(description="My CLI tool")
    >>> # Add global options
    >>> parser.add_global_argument("--verbose", "-v", action="store_true")
    >>> parser.add_global_argument("--output", "-o", type=str)
    >>> # Add subcommands
    >>> cmd1 = parser.add_command("build", help="Build the project")
    >>> cmd1.add_argument("target", help="Build target")
    >>> cmd2 = parser.add_command("test", help="Run tests")
    >>> cmd2.add_argument("--coverage", action="store_true")
    >>> # Parse arguments
    >>> args = parser.parse_args(["--verbose", "build", "release"])
    >>> # args.verbose == True, args.command == "build", args.target == "release"
"""

import argparse
from typing import Any


class TwoStepParser:
    """Argument parser with two-step parsing for flexible global option positioning.

    This parser allows global options to appear before or after subcommands by using
    a two-pass parsing approach:

    1. First pass: Extract global options from anywhere in argv using parse_known_args
    2. Second pass: Parse complete command structure including subcommands

    This enables flexible command structures like:
    - `tool --verbose command arg` (global before)
    - `tool command arg --verbose` (global after)
    - `tool --verbose command --output file arg` (mixed)
    """

    def __init__(
        self,
        description: str | None = None,
        formatter_class: type[argparse.HelpFormatter] = argparse.RawDescriptionHelpFormatter,
        **kwargs: Any,
    ) -> None:
        """Initialize the two-step parser.

        Args:
            description: Description for the main parser
            formatter_class: Formatter class for help output
            **kwargs: Additional arguments passed to ArgumentParser
        """
        self.description = description
        self.formatter_class = formatter_class
        self.parser_kwargs = kwargs

        # Storage for global arguments
        self._global_args: list[tuple[tuple[str, ...], dict[str, Any]]] = []

        # Storage for subcommand parsers
        self._subparsers: dict[str, argparse.ArgumentParser] = {}
        self._subparser_configs: dict[str, dict[str, Any]] = {}

    def add_global_argument(self, *args: str, **kwargs: Any) -> None:
        """Add a global argument that can appear before or after subcommands.

        Args:
            *args: Positional arguments for add_argument (e.g., "--verbose", "-v")
            **kwargs: Keyword arguments for add_argument (e.g., action="store_true")
        """
        self._global_args.append((args, kwargs))

    def add_command(
        self,
        name: str,
        help: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> argparse.ArgumentParser:
        """Add a subcommand parser.

        Args:
            name: Name of the subcommand
            help: Short help text for the subcommand
            description: Long description for the subcommand
            **kwargs: Additional arguments passed to add_parser

        Returns:
            ArgumentParser for the subcommand (can be used to add command-specific arguments)
        """
        # Store configuration for later creation
        self._subparser_configs[name] = {
            "help": help,
            "description": description,
            **kwargs,
        }

        # Create a placeholder parser that will be replaced during parse_args
        # This allows users to add arguments to it before parsing
        placeholder = argparse.ArgumentParser(add_help=False)
        self._subparsers[name] = placeholder
        return placeholder

    def _create_global_parser(self) -> argparse.ArgumentParser:
        """Create parser for global options only (first pass).

        Returns:
            ArgumentParser configured with global options only
        """
        global_parser = argparse.ArgumentParser(add_help=False)
        for args, kwargs in self._global_args:
            global_parser.add_argument(*args, **kwargs)
        return global_parser

    def _create_command_parser(self) -> argparse.ArgumentParser:
        """Create full command parser with subcommands (second pass).

        Returns:
            ArgumentParser configured with global options and subcommands
        """
        command_parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=self.formatter_class,
            add_help=True,
            **self.parser_kwargs,
        )

        # Add global arguments to command parser for help display
        for args, kwargs in self._global_args:
            command_parser.add_argument(*args, **kwargs)

        # Create subparsers
        subparsers_action = command_parser.add_subparsers(
            dest="command",
            help="Command to execute",
            required=True,
        )

        # Create actual subcommand parsers
        for name, config in self._subparser_configs.items():
            # Get the placeholder parser with user-added arguments
            placeholder = self._subparsers[name]

            # Use formatter_class from config if provided, otherwise use default
            parser_config = config.copy()
            if "formatter_class" not in parser_config:
                parser_config["formatter_class"] = self.formatter_class

            # Create the actual subparser
            subparser = subparsers_action.add_parser(
                name,
                **parser_config,
            )

            # Copy arguments from placeholder to actual subparser
            for action in placeholder._actions:
                if action.dest != "help":  # Skip help action
                    subparser._add_action(action)

            # Add global arguments to subparser for help display
            for args, kwargs in self._global_args:
                subparser.add_argument(*args, **kwargs)

        return command_parser

    def parse_args(self, argv: list[str] | None = None) -> argparse.Namespace:
        """Parse arguments using two-step approach.

        Args:
            argv: List of arguments to parse (defaults to sys.argv[1:])

        Returns:
            Namespace containing all parsed arguments
        """
        # First pass: parse global options only
        global_parser = self._create_global_parser()
        global_args, _ = global_parser.parse_known_args(argv)

        # Second pass: parse complete command with subcommands
        command_parser = self._create_command_parser()
        command_args = command_parser.parse_args(argv)

        # Merge results: use global_args for global options, command_args for everything else
        # This ensures global options from anywhere in argv are captured
        result = argparse.Namespace(**vars(command_args))

        # Override with global options from first pass
        for key, value in vars(global_args).items():
            setattr(result, key, value)

        return result
