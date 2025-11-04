"""Unit tests for the config module."""

import argparse
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.config import Args, Config


class TestArgs:
    """Tests for Args dataclass."""

    def test_parse_args_default(self) -> None:
        """Test parsing args with defaults."""
        args = Args.parse_args(["script.py", "namespace"])
        
        assert args.command == "namespace"
        assert args.namespace == []
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_namespace(self) -> None:
        """Test parsing args with namespace."""
        args = Args.parse_args(["script.py", "namespace", "dev"])
        
        assert args.command == "namespace"
        assert args.namespace == ["dev"]
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_all_namespace(self) -> None:
        """Test parsing args with 'all' namespace."""
        args = Args.parse_args(["script.py", "namespace", "all"])
        
        assert args.command == "namespace"
        assert args.namespace == ["all"]
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_multiple_namespaces(self) -> None:
        """Test parsing args with multiple namespaces."""
        args = Args.parse_args(["script.py", "namespace", "test", "release", "dev"])
        
        assert args.command == "namespace"
        assert args.namespace == ["test", "release", "dev"]
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_no_color(self) -> None:
        """Test parsing args with --no-color flag."""
        args = Args.parse_args(["script.py", "namespace", "--no-color"])
        
        assert args.command == "namespace"
        assert args.no_color is True
        assert args.namespace == []
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_search_dirs(self) -> None:
        """Test parsing args with --search-dirs."""
        args = Args.parse_args(["script.py", "namespace", "--search-dirs", "/path1:/path2"])
        
        assert args.command == "namespace"
        assert args.search_dirs == [Path("/path1"), Path("/path2")]
        assert args.namespace == []
        assert args.no_color is False
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_search_dirs_short(self) -> None:
        """Test parsing args with -s short option."""
        args = Args.parse_args(["script.py", "namespace", "-s", "/path"])
        
        assert args.command == "namespace"
        assert args.search_dirs == [Path("/path")]
        assert args.namespace == []
        assert args.no_color is False
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_verbose(self) -> None:
        """Test parsing args with --verbose flag."""
        args = Args.parse_args(["script.py", "namespace", "--verbose"])
        
        assert args.command == "namespace"
        assert args.verbose is True
        assert args.namespace == []
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_verbose_short(self) -> None:
        """Test parsing args with -v short option."""
        args = Args.parse_args(["script.py", "namespace", "-v"])
        
        assert args.command == "namespace"
        assert args.verbose is True
        assert args.namespace == []
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_json(self) -> None:
        """Test parsing args with --json flag."""
        args = Args.parse_args(["script.py", "namespace", "--json"])
        
        assert args.command == "namespace"
        assert args.json_output is True
        assert args.namespace == []
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False

    def test_parse_args_namespace_with_no_color(self) -> None:
        """Test parsing namespace with --no-color flag."""
        args = Args.parse_args(["script.py", "namespace", "dev", "--no-color"])
        
        assert args.command == "namespace"
        assert args.namespace == ["dev"]
        assert args.no_color is True
        assert args.verbose is False
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_namespace_with_verbose(self) -> None:
        """Test parsing namespace with --verbose flag."""
        args = Args.parse_args(["script.py", "namespace", "dev", "--verbose"])
        
        assert args.command == "namespace"
        assert args.namespace == ["dev"]
        assert args.no_color is False
        assert args.verbose is True
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_namespace_with_search_dirs(self) -> None:
        """Test parsing namespace with --search-dirs."""
        args = Args.parse_args(["script.py", "namespace", "dev", "--search-dirs", "/path"])
        
        assert args.command == "namespace"
        assert args.namespace == ["dev"]
        assert args.no_color is False
        assert args.verbose is False
        assert args.search_dirs == [Path("/path")]
        assert args.json_output is False

    def test_parse_args_global_option_before_subcommand(self) -> None:
        """Global option --json works before subcommand."""
        args = Args.parse_args(["script.py", "--json", "search", "test"])
        
        assert args.command == "search"
        assert args.json_output is True
        assert args.patterns == ["test"]

    def test_parse_args_global_option_after_subcommand(self) -> None:
        """Global option --json works after subcommand."""
        args = Args.parse_args(["script.py", "search", "test", "--json"])
        
        assert args.command == "search"
        assert args.json_output is True
        assert args.patterns == ["test"]

    def test_parse_args_multiple_global_options_before_subcommand(self) -> None:
        """Multiple global options work before subcommand."""
        args = Args.parse_args(["script.py", "--json", "--verbose", "search", "test"])
        
        assert args.command == "search"
        assert args.json_output is True
        assert args.verbose is True
        assert args.patterns == ["test"]

    def test_parse_args_multiple_global_options_after_subcommand(self) -> None:
        """Multiple global options work after subcommand."""
        args = Args.parse_args(["script.py", "search", "test", "--json", "--verbose"])
        
        assert args.command == "search"
        assert args.json_output is True
        assert args.verbose is True
        assert args.patterns == ["test"]

    def test_parse_args_global_options_mixed_positions(self) -> None:
        """Global options work in mixed positions (before and after subcommand)."""
        args = Args.parse_args(["script.py", "--json", "search", "test", "--verbose"])
        
        assert args.command == "search"
        assert args.json_output is True
        assert args.verbose is True
        assert args.patterns == ["test"]

    def test_parse_args_no_color_before_subcommand(self) -> None:
        """Global option --no-color works before subcommand."""
        args = Args.parse_args(["script.py", "--no-color", "namespace", "dev"])
        
        assert args.command == "namespace"
        assert args.namespace == ["dev"]
        assert args.no_color is True

    def test_parse_args_search_dirs_before_subcommand(self) -> None:
        """Global option --search-dirs works before subcommand."""
        args = Args.parse_args(["script.py", "--search-dirs", "/path1:/path2", "namespace"])
        
        assert args.command == "namespace"
        assert args.search_dirs == [Path("/path1"), Path("/path2")]

    def test_parse_args_search_dirs_short_before_subcommand(self) -> None:
        """Global option -s works before subcommand."""
        args = Args.parse_args(["script.py", "-s", "/path", "namespace", "main"])
        
        assert args.command == "namespace"
        assert args.namespace == ["main"]
        assert args.search_dirs == [Path("/path")]

    def test_parse_args_verbose_before_subcommand(self) -> None:
        """Global option --verbose works before subcommand."""
        args = Args.parse_args(["script.py", "--verbose", "search", "pattern"])
        
        assert args.command == "search"
        assert args.verbose is True
        assert args.patterns == ["pattern"]

    def test_parse_args_verbose_short_before_subcommand(self) -> None:
        """Global option -v works before subcommand."""
        args = Args.parse_args(["script.py", "-v", "search", "pattern"])
        
        assert args.command == "search"
        assert args.verbose is True
        assert args.patterns == ["pattern"]

    def test_parse_args_group_pattern_before_subcommand(self) -> None:
        """Global option --group-pattern works before subcommand."""
        args = Args.parse_args(["script.py", "--group-pattern", "custom.*pattern", "namespace"])
        
        assert args.command == "namespace"
        assert args.group_pattern == "custom.*pattern"

    def test_parse_args_completion_before_subcommand(self) -> None:
        """Global option --completion works before subcommand."""
        args = Args.parse_args(["script.py", "--completion", "bash", "namespace"])
        
        assert args.command == "namespace"
        assert args.completion == "bash"

    def test_parse_args_all_global_options_before_subcommand(self) -> None:
        """All global options work before subcommand."""
        args = Args.parse_args([
            "script.py",
            "--no-color",
            "--search-dirs", "/path",
            "--verbose",
            "--json",
            "--group-pattern", "test",
            "search",
            "pattern"
        ])
        
        assert args.command == "search"
        assert args.no_color is True
        assert args.search_dirs == [Path("/path")]
        assert args.verbose is True
        assert args.json_output is True
        assert args.group_pattern == "test"
        assert args.patterns == ["pattern"]

    def test_main_help_shows_global_options(self) -> None:
        """Main help (taskfile-help --help) displays all global options."""
        # Create the parser as parse_args does
        command_parser = argparse.ArgumentParser(
            description="Dynamic Taskfile help generator",
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        Args._add_global_arguments(command_parser, Args._list_of_paths)
        subparsers = command_parser.add_subparsers(dest="command", help="Command to execute", required=True)
        Args._create_namespace_parser(subparsers, Args._list_of_paths)
        Args._create_search_parser(subparsers, Args._list_of_paths)
        
        help_text = command_parser.format_help()
        
        # Verify all global options appear in help
        assert "--no-color" in help_text
        assert "--search-dirs" in help_text
        assert "-s SEARCH_DIRS" in help_text
        assert "--verbose" in help_text
        assert "-v" in help_text
        assert "--json" in help_text
        assert "--completion" in help_text
        assert "--install-completion" in help_text
        assert "--group-pattern" in help_text
        
        # Verify help descriptions
        assert "Disable colored output" in help_text
        assert "Show verbose output" in help_text
        assert "Output tasks in JSON format" in help_text

    def test_namespace_help_shows_global_options(self) -> None:
        """Namespace subcommand help (taskfile-help namespace --help) displays all global options."""
        # Create the parser as parse_args does
        command_parser = argparse.ArgumentParser(
            description="Dynamic Taskfile help generator",
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        Args._add_global_arguments(command_parser, Args._list_of_paths)
        subparsers = command_parser.add_subparsers(dest="command", help="Command to execute", required=True)
        Args._create_namespace_parser(subparsers, Args._list_of_paths)
        Args._create_search_parser(subparsers, Args._list_of_paths)
        
        # Get the namespace subparser via the choices dict
        namespace_parser = subparsers.choices['namespace']
        help_text = namespace_parser.format_help()
        
        # Verify all global options appear in namespace help
        assert "--no-color" in help_text
        assert "--search-dirs" in help_text
        assert "-s SEARCH_DIRS" in help_text
        assert "--verbose" in help_text
        assert "-v" in help_text
        assert "--json" in help_text
        assert "--completion" in help_text
        assert "--install-completion" in help_text
        assert "--group-pattern" in help_text
        
        # Verify help descriptions
        assert "Disable colored output" in help_text
        assert "Show verbose output" in help_text
        assert "Output tasks in JSON format" in help_text

    def test_search_help_shows_global_options(self) -> None:
        """Search subcommand help (taskfile-help search --help) displays all global options."""
        # Create the parser as parse_args does
        command_parser = argparse.ArgumentParser(
            description="Dynamic Taskfile help generator",
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        Args._add_global_arguments(command_parser, Args._list_of_paths)
        subparsers = command_parser.add_subparsers(dest="command", help="Command to execute", required=True)
        Args._create_namespace_parser(subparsers, Args._list_of_paths)
        Args._create_search_parser(subparsers, Args._list_of_paths)
        
        # Get the search subparser via the choices dict
        search_parser = subparsers.choices['search']
        help_text = search_parser.format_help()
        
        # Verify all global options appear in search help
        assert "--no-color" in help_text
        assert "--search-dirs" in help_text
        assert "-s SEARCH_DIRS" in help_text
        assert "--verbose" in help_text
        assert "-v" in help_text
        assert "--json" in help_text
        assert "--completion" in help_text
        assert "--install-completion" in help_text
        assert "--group-pattern" in help_text
        
        # Verify help descriptions
        assert "Disable colored output" in help_text
        assert "Show verbose output" in help_text
        assert "Output tasks in JSON format" in help_text
        
        # Verify search-specific option is also present
        assert "--regex" in help_text


class TestConfig:
    """Tests for Config class."""

    def test_config_default_search_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config with default search directory."""
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == tmp_path

    def test_config_search_dirs_from_args(self, tmp_path: Path) -> None:
        """Test config with search dirs from command line."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        config = Config(["script.py", "namespace", "-s", f"{dir1}:{dir2}"])
        
        assert len(config.discovery.search_dirs) == 2
        assert dir1 in config.discovery.search_dirs
        assert dir2 in config.discovery.search_dirs

    def test_config_search_dirs_from_pyproject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config with search dirs from pyproject.toml as list."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = [".", "../other"]
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        # Should have at least current directory
        assert len(config.discovery.search_dirs) >= 1
        assert tmp_path in config.discovery.search_dirs

    def test_config_search_dirs_from_pyproject_single_string(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config with search dirs from pyproject.toml as single string."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = "."
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == tmp_path

    def test_config_search_dirs_from_pyproject_empty_string(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config with search dirs from pyproject.toml as empty string."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = ""
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        # Empty string should default to current directory
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == tmp_path

    def test_config_search_dirs_from_pyproject_list_with_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config with search dirs from pyproject.toml list containing empty strings."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = [".", "", "../other"]
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        # Empty strings should be filtered out
        assert len(config.discovery.search_dirs) >= 1
        assert tmp_path in config.discovery.search_dirs

    def test_config_args_override_pyproject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test command line args override pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = [".", "../other"]
""")
        monkeypatch.chdir(tmp_path)
        
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        
        config = Config(["script.py", "namespace", "-s", str(dir1)])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == dir1

    @patch("sys.stdout.isatty")
    def test_config_colorize_tty(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """Test colorize enabled when output is TTY."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is True

    @patch("sys.stdout.isatty")
    def test_config_colorize_no_tty(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """Test colorize disabled when output is not TTY."""
        mock_isatty.return_value = False
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch("sys.stdout.isatty")
    def test_config_colorize_no_color_flag(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """Test colorize disabled with --no-color flag."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace", "--no-color"])
        
        assert config.colorize is False

    def test_config_all_namespace(self, tmp_path: Path) -> None:
        """Test 'all' namespace."""
        config = Config(["script.py", "namespace", "all"])
        
        assert config.namespace == ["all"]

    def test_config_namespace_property(self, tmp_path: Path) -> None:
        """Test namespace property."""
        config = Config(["script.py", "namespace", "dev"])
        
        assert config.namespace == ["dev"]

    def test_config_removes_duplicate_search_dirs(self, tmp_path: Path) -> None:
        """Test duplicate search directories are removed."""
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        
        config = Config(["script.py", "namespace", "-s", f"{dir1}:{dir1}:{dir1}"])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == dir1

    def test_config_removes_duplicate_search_dirs_order(self, tmp_path: Path) -> None:
        """Test duplicate search directories preserve first occurrence order."""
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        
        config = Config(["script.py", "namespace", "-s", f"{dir1}:{dir2}:{dir1}"])
        
        assert len(config.discovery.search_dirs) == 2
        assert config.discovery.search_dirs[0] == dir1
        assert config.discovery.search_dirs[1] == dir2

    def test_config_resolves_relative_paths(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test relative paths are resolved to absolute paths."""
        monkeypatch.chdir(tmp_path)
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        config = Config(["script.py", "namespace", "-s", "./subdir"])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == subdir

    def test_config_empty_search_dirs_defaults_to_cwd(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test empty search dirs defaults to current directory."""
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace", "-s", ""])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == tmp_path

    def test_config_search_dirs_from_taskfile_help_yml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config with search dirs from taskfile_help.yml."""
        config_file = tmp_path / "taskfile_help.yml"
        config_file.write_text("""
search-dirs:
  - "."
  - "../other"
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        # Should have at least current directory
        assert len(config.discovery.search_dirs) >= 1
        assert tmp_path in config.discovery.search_dirs

    def test_config_taskfile_help_yml_takes_precedence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test taskfile_help.yml takes precedence over pyproject.toml."""
        # Create both config files with different values
        yaml_config = tmp_path / "taskfile_help.yml"
        yaml_config.write_text("""
search-dirs:
  - "yaml_dir"
""")
        
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = ["toml_dir"]
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        # Should use the YAML config (first in search order)
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == tmp_path / "yaml_dir"

    def test_config_no_color_from_taskfile_help_yml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test no-color setting from taskfile_help.yml."""
        config_file = tmp_path / "taskfile_help.yml"
        config_file.write_text("""
no-color: true
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    def test_config_group_pattern_from_taskfile_help_yml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test group-pattern setting from taskfile_help.yml."""
        config_file = tmp_path / "taskfile_help.yml"
        config_file.write_text(r"""
group-pattern: "\\s*#\\s*---\\s*(.+?)\\s*---"
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert config.group_pattern == r"\s*#\s*---\s*(.+?)\s*---"
