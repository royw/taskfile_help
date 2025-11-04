"""Tests for TwoStepParser."""

import argparse

import pytest

from taskfile_help.two_step_parser import TwoStepParser


class TestTwoStepParser:
    """Test the TwoStepParser class."""

    def test_basic_usage(self) -> None:
        """Test basic parser creation and usage."""
        parser = TwoStepParser(description="Test CLI")
        
        # Add global options
        parser.add_global_argument("--verbose", "-v", action="store_true", help="Verbose output")
        parser.add_global_argument("--output", "-o", type=str, help="Output file")
        
        # Add commands
        build_cmd = parser.add_command("build", help="Build the project")
        build_cmd.add_argument("target", help="Build target")
        
        test_cmd = parser.add_command("test", help="Run tests")
        test_cmd.add_argument("--coverage", action="store_true", help="Enable coverage")
        
        # Parse with global option before command
        args = parser.parse_args(["--verbose", "build", "release"])
        
        assert args.verbose is True
        assert args.command == "build"
        assert args.target == "release"

    def test_global_option_after_command(self) -> None:
        """Test global option placed after command."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        
        cmd = parser.add_command("test")
        cmd.add_argument("pattern", nargs="?")
        
        # Global option after command
        args = parser.parse_args(["test", "unit", "--verbose"])
        
        assert args.verbose is True
        assert args.command == "test"
        assert args.pattern == "unit"

    def test_global_option_before_command(self) -> None:
        """Test global option placed before command."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        
        cmd = parser.add_command("test")
        cmd.add_argument("pattern", nargs="?")
        
        # Global option before command
        args = parser.parse_args(["--verbose", "test", "unit"])
        
        assert args.verbose is True
        assert args.command == "test"
        assert args.pattern == "unit"

    def test_mixed_global_options(self) -> None:
        """Test global options in mixed positions."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", "-v", action="store_true")
        parser.add_global_argument("--output", "-o", type=str)
        parser.add_global_argument("--format", type=str)
        
        cmd = parser.add_command("export")
        cmd.add_argument("source", help="Source file")
        
        # Mixed positions
        args = parser.parse_args(["--verbose", "export", "data.txt", "--output", "out.json", "--format", "json"])
        
        assert args.verbose is True
        assert args.output == "out.json"
        assert args.format == "json"
        assert args.command == "export"
        assert args.source == "data.txt"

    def test_multiple_commands(self) -> None:
        """Test parser with multiple commands."""
        parser = TwoStepParser()
        parser.add_global_argument("--config", type=str)
        
        build_cmd = parser.add_command("build")
        build_cmd.add_argument("--release", action="store_true")
        
        test_cmd = parser.add_command("test")
        test_cmd.add_argument("--coverage", action="store_true")
        
        deploy_cmd = parser.add_command("deploy")
        deploy_cmd.add_argument("environment", choices=["dev", "prod"])
        
        # Test build command
        args = parser.parse_args(["build", "--release", "--config", "build.yml"])
        assert args.command == "build"
        assert args.release is True
        assert args.config == "build.yml"
        
        # Test deploy command
        args = parser.parse_args(["--config", "deploy.yml", "deploy", "prod"])
        assert args.command == "deploy"
        assert args.environment == "prod"
        assert args.config == "deploy.yml"

    def test_short_and_long_options(self) -> None:
        """Test both short and long option forms."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", "-v", action="store_true")
        parser.add_global_argument("--output", "-o", type=str)
        
        cmd = parser.add_command("process")
        cmd.add_argument("file")
        
        # Test short options
        args = parser.parse_args(["-v", "process", "data.txt", "-o", "out.txt"])
        assert args.verbose is True
        assert args.output == "out.txt"
        
        # Test long options
        args = parser.parse_args(["--verbose", "process", "data.txt", "--output", "out.txt"])
        assert args.verbose is True
        assert args.output == "out.txt"

    def test_command_specific_arguments(self) -> None:
        """Test that command-specific arguments are properly isolated."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        
        build_cmd = parser.add_command("build")
        build_cmd.add_argument("--optimize", action="store_true")
        
        test_cmd = parser.add_command("test")
        test_cmd.add_argument("--coverage", action="store_true")
        
        # Build command should have optimize but not coverage
        args = parser.parse_args(["build", "--optimize"])
        assert args.command == "build"
        assert args.optimize is True
        assert not hasattr(args, "coverage")
        
        # Test command should have coverage but not optimize
        args = parser.parse_args(["test", "--coverage"])
        assert args.command == "test"
        assert args.coverage is True
        assert not hasattr(args, "optimize")

    def test_optional_arguments(self) -> None:
        """Test optional command arguments with nargs."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        
        cmd = parser.add_command("search")
        cmd.add_argument("patterns", nargs="*", help="Search patterns")
        
        # No patterns
        args = parser.parse_args(["search"])
        assert args.command == "search"
        assert args.patterns == []
        
        # Multiple patterns
        args = parser.parse_args(["search", "foo", "bar", "baz"])
        assert args.patterns == ["foo", "bar", "baz"]
        
        # With global option
        args = parser.parse_args(["--verbose", "search", "foo", "bar"])
        assert args.verbose is True
        assert args.patterns == ["foo", "bar"]

    def test_required_arguments(self) -> None:
        """Test required command arguments."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        
        cmd = parser.add_command("copy")
        cmd.add_argument("source", help="Source file")
        cmd.add_argument("dest", help="Destination file")
        
        args = parser.parse_args(["copy", "in.txt", "out.txt"])
        assert args.source == "in.txt"
        assert args.dest == "out.txt"
        
        # Should fail without required arguments
        with pytest.raises(SystemExit):
            parser.parse_args(["copy", "in.txt"])

    def test_default_values(self) -> None:
        """Test default values for global options."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true", default=False)
        parser.add_global_argument("--level", type=int, default=1)
        
        cmd = parser.add_command("run")
        
        # Without specifying options
        args = parser.parse_args(["run"])
        assert args.verbose is False
        assert args.level == 1
        
        # With options specified
        args = parser.parse_args(["--verbose", "--level", "3", "run"])
        assert args.verbose is True
        assert args.level == 3

    def test_formatter_class(self) -> None:
        """Test custom formatter class."""
        parser = TwoStepParser(
            description="Test CLI",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_global_argument("--verbose", action="store_true")
        cmd = parser.add_command("test")
        
        # Just verify it doesn't crash
        args = parser.parse_args(["test"])
        assert args.command == "test"

    def test_no_command_fails(self) -> None:
        """Test that parser requires a command."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        parser.add_command("test")
        
        # Should fail without command
        with pytest.raises(SystemExit):
            parser.parse_args(["--verbose"])

    def test_command_with_choices(self) -> None:
        """Test command argument with choices."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", action="store_true")
        
        cmd = parser.add_command("deploy")
        cmd.add_argument("env", choices=["dev", "staging", "prod"])
        
        args = parser.parse_args(["deploy", "staging"])
        assert args.env == "staging"
        
        # Invalid choice should fail
        with pytest.raises(SystemExit):
            parser.parse_args(["deploy", "invalid"])

    def test_multiple_global_options_same_position(self) -> None:
        """Test multiple global options in the same position."""
        parser = TwoStepParser()
        parser.add_global_argument("--verbose", "-v", action="store_true")
        parser.add_global_argument("--debug", "-d", action="store_true")
        parser.add_global_argument("--quiet", "-q", action="store_true")
        
        cmd = parser.add_command("run")
        cmd.add_argument("script")
        
        # All before command
        args = parser.parse_args(["--verbose", "--debug", "run", "test.sh"])
        assert args.verbose is True
        assert args.debug is True
        assert args.quiet is False
        
        # All after command
        args = parser.parse_args(["run", "test.sh", "-v", "-d", "-q"])
        assert args.verbose is True
        assert args.debug is True
        assert args.quiet is True
