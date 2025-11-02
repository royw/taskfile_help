"""Unit tests for environment variable configuration."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.config import Config


class TestEnvironmentVariables:
    """Tests for environment variable configuration."""

    @patch.dict("os.environ", {"NO_COLOR": "1"})
    @patch("sys.stdout.isatty")
    def test_no_color_env_var(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """NO_COLOR environment variable disables colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"NO_COLOR": ""})
    @patch("sys.stdout.isatty")
    def test_no_color_env_var_empty(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """Empty NO_COLOR environment variable does not disable colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is True

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "true"})
    @patch("sys.stdout.isatty")
    def test_taskfile_help_no_color_true(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """TASKFILE_HELP_NO_COLOR=true disables colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "1"})
    @patch("sys.stdout.isatty")
    def test_taskfile_help_no_color_one(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """TASKFILE_HELP_NO_COLOR=1 disables colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "yes"})
    @patch("sys.stdout.isatty")
    def test_taskfile_help_no_color_yes(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """TASKFILE_HELP_NO_COLOR=yes disables colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "false"})
    @patch("sys.stdout.isatty")
    def test_taskfile_help_no_color_false(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """TASKFILE_HELP_NO_COLOR=false does not disable colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is True

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": "/tmp:/var/tmp"})
    def test_search_dirs_env_var(self, tmp_path: Path) -> None:
        """TASKFILE_HELP_SEARCH_DIRS environment variable sets search directories."""
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 2
        assert Path("/tmp") in config.discovery.search_dirs
        assert Path("/var/tmp") in config.discovery.search_dirs

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": "/tmp"})
    def test_search_dirs_env_var_single(self, tmp_path: Path) -> None:
        """TASKFILE_HELP_SEARCH_DIRS with single directory."""
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 1
        assert Path("/tmp") in config.discovery.search_dirs

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": ""})
    def test_search_dirs_env_var_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Empty TASKFILE_HELP_SEARCH_DIRS defaults to current directory."""
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == tmp_path

    @patch.dict("os.environ", {"TASKFILE_HELP_GROUP_PATTERN": r"\s*##\s*(.+?)\s*##"})
    def test_group_pattern_env_var(self, tmp_path: Path) -> None:
        """TASKFILE_HELP_GROUP_PATTERN environment variable sets group pattern."""
        config = Config(["script.py", "namespace"])
        
        assert config.group_pattern == r"\s*##\s*(.+?)\s*##"

    @patch.dict("os.environ", {}, clear=True)
    def test_group_pattern_env_var_not_set(self, tmp_path: Path) -> None:
        """Missing TASKFILE_HELP_GROUP_PATTERN uses default pattern."""
        config = Config(["script.py", "namespace"])
        
        assert config.group_pattern == r"\s*#\s*===\s*(.+?)\s*==="


class TestEnvironmentVariablePriority:
    """Tests for environment variable priority order."""

    @patch.dict("os.environ", {"NO_COLOR": "1"})
    @patch("sys.stdout.isatty")
    def test_cli_overrides_no_color_env(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """Command-line --no-color flag takes precedence over NO_COLOR env var."""
        mock_isatty.return_value = True
        
        # Even though NO_COLOR is set, CLI flag should control behavior
        config = Config(["script.py", "namespace", "--no-color"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": "/tmp:/var/tmp"})
    def test_cli_overrides_search_dirs_env(self, tmp_path: Path) -> None:
        """Command-line --search-dirs overrides TASKFILE_HELP_SEARCH_DIRS."""
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        
        config = Config(["script.py", "namespace", "-s", str(dir1)])
        
        assert len(config.discovery.search_dirs) == 1
        assert config.discovery.search_dirs[0] == dir1

    @patch.dict("os.environ", {"TASKFILE_HELP_GROUP_PATTERN": r"\s*##\s*(.+?)\s*##"})
    def test_cli_overrides_group_pattern_env(self, tmp_path: Path) -> None:
        """Command-line --group-pattern overrides TASKFILE_HELP_GROUP_PATTERN."""
        config = Config(["script.py", "namespace", "--group-pattern", r"\s*#\s*---\s*(.+?)\s*---"])
        
        assert config.group_pattern == r"\s*#\s*---\s*(.+?)\s*---"

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": "/tmp"})
    def test_env_overrides_pyproject(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment variable overrides pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = [".", "../other"]
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 1
        assert Path("/tmp") in config.discovery.search_dirs

    @patch.dict("os.environ", {"NO_COLOR": "1", "TASKFILE_HELP_NO_COLOR": "false"})
    @patch("sys.stdout.isatty")
    def test_no_color_takes_precedence_over_taskfile_help_no_color(
        self, mock_isatty: Mock, tmp_path: Path
    ) -> None:
        """NO_COLOR takes precedence over TASKFILE_HELP_NO_COLOR."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        # NO_COLOR should win even though TASKFILE_HELP_NO_COLOR is "false"
        assert config.colorize is False


class TestEnvironmentVariablesWithPyproject:
    """Tests for environment variables combined with pyproject.toml."""

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "true"})
    @patch("sys.stdout.isatty")
    def test_env_no_color_overrides_pyproject(
        self, mock_isatty: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Environment NO_COLOR overrides pyproject.toml no-color setting."""
        mock_isatty.return_value = True
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
no-color = false
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"TASKFILE_HELP_GROUP_PATTERN": r"\s*##\s*(.+?)\s*##"})
    def test_env_group_pattern_overrides_pyproject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Environment TASKFILE_HELP_GROUP_PATTERN overrides pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
group-pattern = "\\\\s*#\\\\s*---\\\\s*(.+?)\\\\s*---"
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert config.group_pattern == r"\s*##\s*(.+?)\s*##"

    @patch("sys.stdout.isatty")
    def test_pyproject_no_color_when_no_env(
        self, mock_isatty: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """pyproject.toml no-color is used when no environment variable is set."""
        mock_isatty.return_value = True
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
no-color = true
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    def test_pyproject_group_pattern_when_no_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """pyproject.toml group-pattern is used when no environment variable is set."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
group-pattern = "\\\\s*##\\\\s*(.+?)\\\\s*##"
""")
        monkeypatch.chdir(tmp_path)
        
        config = Config(["script.py", "namespace"])
        
        assert config.group_pattern == r"\s*##\s*(.+?)\s*##"

    def test_pyproject_search_dirs_when_no_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """pyproject.toml search-dirs is used when no environment variable is set."""
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


class TestEnvironmentVariableEdgeCases:
    """Tests for edge cases in environment variable handling."""

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": ":/tmp:"})
    def test_search_dirs_with_empty_entries(self, tmp_path: Path) -> None:
        """TASKFILE_HELP_SEARCH_DIRS with empty entries filters them out."""
        config = Config(["script.py", "namespace"])
        
        # Empty entries should be filtered out
        assert len(config.discovery.search_dirs) == 1
        assert Path("/tmp") in config.discovery.search_dirs

    @patch.dict("os.environ", {"TASKFILE_HELP_SEARCH_DIRS": "/tmp:/tmp:/var/tmp"})
    def test_search_dirs_removes_duplicates(self, tmp_path: Path) -> None:
        """TASKFILE_HELP_SEARCH_DIRS removes duplicate directories."""
        config = Config(["script.py", "namespace"])
        
        assert len(config.discovery.search_dirs) == 2
        assert Path("/tmp") in config.discovery.search_dirs
        assert Path("/var/tmp") in config.discovery.search_dirs

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "TRUE"})
    @patch("sys.stdout.isatty")
    def test_no_color_case_insensitive(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """TASKFILE_HELP_NO_COLOR is case-insensitive."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False

    @patch.dict("os.environ", {"TASKFILE_HELP_NO_COLOR": "YES"})
    @patch("sys.stdout.isatty")
    def test_no_color_yes_uppercase(self, mock_isatty: Mock, tmp_path: Path) -> None:
        """TASKFILE_HELP_NO_COLOR=YES (uppercase) disables colors."""
        mock_isatty.return_value = True
        
        config = Config(["script.py", "namespace"])
        
        assert config.colorize is False
