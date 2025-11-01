"""Unit tests for the config module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.config import Args, Config, _load_pyproject_config


class TestLoadPyprojectConfig:
    """Tests for _load_pyproject_config function."""

    def test_load_config_with_search_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config with search-dirs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = [".", "../shared"]
""")
        monkeypatch.chdir(tmp_path)
        
        config = _load_pyproject_config()
        
        assert "search-dirs" in config
        assert config["search-dirs"] == [".", "../shared"]

    def test_load_config_no_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config when pyproject.toml doesn't exist."""
        monkeypatch.chdir(tmp_path)
        
        config = _load_pyproject_config()
        
        assert config == {}

    def test_load_config_no_tool_section(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config when tool section doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"
""")
        monkeypatch.chdir(tmp_path)
        
        config = _load_pyproject_config()
        
        assert config == {}

    def test_load_config_invalid_toml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config with invalid TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("invalid toml [[[")
        monkeypatch.chdir(tmp_path)
        
        config = _load_pyproject_config()
        
        assert config == {}


class TestArgs:
    """Tests for Args dataclass."""

    def test_parse_args_default(self) -> None:
        """Test parsing args with defaults."""
        args = Args.parse_args(["script.py", "namespace"])
        
        assert args.command == "namespace"
        assert args.namespace == ""
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_namespace(self) -> None:
        """Test parsing args with namespace."""
        args = Args.parse_args(["script.py", "namespace", "dev"])
        
        assert args.command == "namespace"
        assert args.namespace == "dev"
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_all_namespace(self) -> None:
        """Test parsing args with 'all' namespace."""
        args = Args.parse_args(["script.py", "namespace", "all"])
        
        assert args.command == "namespace"
        assert args.namespace == "all"
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_no_color(self) -> None:
        """Test parsing args with --no-color flag."""
        args = Args.parse_args(["script.py", "namespace", "--no-color"])
        
        assert args.command == "namespace"
        assert args.no_color is True
        assert args.namespace == ""
        assert args.search_dirs is None
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_search_dirs(self) -> None:
        """Test parsing args with --search-dirs."""
        args = Args.parse_args(["script.py", "namespace", "--search-dirs", "/path1:/path2"])
        
        assert args.command == "namespace"
        assert args.search_dirs == [Path("/path1"), Path("/path2")]
        assert args.namespace == ""
        assert args.no_color is False
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_search_dirs_short(self) -> None:
        """Test parsing args with -s short option."""
        args = Args.parse_args(["script.py", "namespace", "-s", "/path"])
        
        assert args.command == "namespace"
        assert args.search_dirs == [Path("/path")]
        assert args.namespace == ""
        assert args.no_color is False
        assert args.verbose is False
        assert args.json_output is False

    def test_parse_args_verbose(self) -> None:
        """Test parsing args with --verbose flag."""
        args = Args.parse_args(["script.py", "namespace", "--verbose"])
        
        assert args.command == "namespace"
        assert args.verbose is True
        assert args.namespace == ""
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_verbose_short(self) -> None:
        """Test parsing args with -v short option."""
        args = Args.parse_args(["script.py", "namespace", "-v"])
        
        assert args.command == "namespace"
        assert args.verbose is True
        assert args.namespace == ""
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_json(self) -> None:
        """Test parsing args with --json flag."""
        args = Args.parse_args(["script.py", "namespace", "--json"])
        
        assert args.command == "namespace"
        assert args.json_output is True
        assert args.namespace == ""
        assert args.no_color is False
        assert args.search_dirs is None
        assert args.verbose is False

    def test_parse_args_namespace_with_no_color(self) -> None:
        """Test parsing namespace with --no-color flag."""
        args = Args.parse_args(["script.py", "namespace", "dev", "--no-color"])
        
        assert args.command == "namespace"
        assert args.namespace == "dev"
        assert args.no_color is True
        assert args.verbose is False
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_namespace_with_verbose(self) -> None:
        """Test parsing namespace with --verbose flag."""
        args = Args.parse_args(["script.py", "namespace", "dev", "--verbose"])
        
        assert args.command == "namespace"
        assert args.namespace == "dev"
        assert args.no_color is False
        assert args.verbose is True
        assert args.search_dirs is None
        assert args.json_output is False

    def test_parse_args_namespace_with_search_dirs(self) -> None:
        """Test parsing namespace with --search-dirs."""
        args = Args.parse_args(["script.py", "namespace", "dev", "--search-dirs", "/path"])
        
        assert args.command == "namespace"
        assert args.namespace == "dev"
        assert args.no_color is False
        assert args.verbose is False
        assert args.search_dirs == [Path("/path")]
        assert args.json_output is False


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
        
        assert config.namespace == "all"

    def test_config_namespace_property(self, tmp_path: Path) -> None:
        """Test namespace property."""
        config = Config(["script.py", "namespace", "dev"])
        
        assert config.namespace == "dev"

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
