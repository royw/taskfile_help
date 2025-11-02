"""Unit tests for ConfigFile protocol and implementations."""

from pathlib import Path

import pytest

from taskfile_help.config import (
    PyProjectConfigFile,
    TaskfileHelpConfigFile,
    get_config_file,
)


class TestPyProjectConfigFile:
    """Tests for PyProjectConfigFile class."""

    def test_load_config_with_search_dirs(self, tmp_path: Path) -> None:
        """Load config with search-dirs from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
search-dirs = [".", "../shared"]
""")

        config_file = PyProjectConfigFile(pyproject)
        config = config_file.load_config()

        assert "search-dirs" in config
        assert config["search-dirs"] == [".", "../shared"]

    def test_load_config_with_no_color(self, tmp_path: Path) -> None:
        """Load config with no-color setting from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.taskfile-help]
no-color = true
""")

        config_file = PyProjectConfigFile(pyproject)
        config = config_file.load_config()

        assert "no-color" in config
        assert config["no-color"] is True

    def test_load_config_with_group_pattern(self, tmp_path: Path) -> None:
        """Load config with group-pattern from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(r"""
[tool.taskfile-help]
group-pattern = "\\s*#\\s*---\\s*(.+?)\\s*---"
""")

        config_file = PyProjectConfigFile(pyproject)
        config = config_file.load_config()

        assert "group-pattern" in config
        assert config["group-pattern"] == r"\s*#\s*---\s*(.+?)\s*---"

    def test_load_config_no_file(self, tmp_path: Path) -> None:
        """Load config when pyproject.toml doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"

        config_file = PyProjectConfigFile(pyproject)
        config = config_file.load_config()

        assert config == {}

    def test_load_config_no_tool_section(self, tmp_path: Path) -> None:
        """Load config when tool section doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"
""")

        config_file = PyProjectConfigFile(pyproject)
        config = config_file.load_config()

        assert config == {}

    def test_load_config_invalid_toml(self, tmp_path: Path) -> None:
        """Load config with invalid TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("invalid toml [[[")

        config_file = PyProjectConfigFile(pyproject)
        config = config_file.load_config()

        assert config == {}


class TestTaskfileHelpConfigFile:
    """Tests for TaskfileHelpConfigFile class."""

    def test_load_config_with_search_dirs(self, tmp_path: Path) -> None:
        """Load config with search-dirs from taskfile_help.yml."""
        config_file_path = tmp_path / "taskfile_help.yml"
        config_file_path.write_text("""
search-dirs:
  - "."
  - "../shared"
""")

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert "search-dirs" in config
        assert config["search-dirs"] == [".", "../shared"]

    def test_load_config_with_no_color(self, tmp_path: Path) -> None:
        """Load config with no-color setting from taskfile_help.yml."""
        config_file_path = tmp_path / "taskfile_help.yml"
        config_file_path.write_text("""
no-color: true
""")

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert "no-color" in config
        assert config["no-color"] is True

    def test_load_config_with_group_pattern(self, tmp_path: Path) -> None:
        """Load config with group-pattern from taskfile_help.yml."""
        config_file_path = tmp_path / "taskfile_help.yml"
        config_file_path.write_text(r"""
group-pattern: "\\s*#\\s*---\\s*(.+?)\\s*---"
""")

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert "group-pattern" in config
        assert config["group-pattern"] == r"\s*#\s*---\s*(.+?)\s*---"

    def test_load_config_no_file(self, tmp_path: Path) -> None:
        """Load config when taskfile_help.yml doesn't exist."""
        config_file_path = tmp_path / "taskfile_help.yml"

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert config == {}

    def test_load_config_empty_file(self, tmp_path: Path) -> None:
        """Load config from empty taskfile_help.yml."""
        config_file_path = tmp_path / "taskfile_help.yml"
        config_file_path.write_text("")

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert config == {}

    def test_load_config_invalid_yaml(self, tmp_path: Path) -> None:
        """Load config with invalid YAML."""
        config_file_path = tmp_path / "taskfile_help.yml"
        config_file_path.write_text("invalid: yaml: [[[")

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert config == {}

    def test_load_config_with_all_settings(self, tmp_path: Path) -> None:
        """Load config with all supported settings from taskfile_help.yml."""
        config_file_path = tmp_path / "taskfile_help.yml"
        config_file_path.write_text("""
search-dirs:
  - "."
  - "taskfiles"
no-color: false
group-pattern: "\\\\s*#\\\\s*===\\\\s*(.+?)\\\\s*==="
""")

        config_file = TaskfileHelpConfigFile(config_file_path)
        config = config_file.load_config()

        assert config["search-dirs"] == [".", "taskfiles"]
        assert config["no-color"] is False
        assert "group-pattern" in config


class TestGetConfigFile:
    """Tests for get_config_file factory function."""

    def test_get_config_file_taskfile_help_yml_first(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Get config file when taskfile_help.yml exists (takes precedence)."""
        monkeypatch.chdir(tmp_path)

        # Create both config files
        (tmp_path / "taskfile_help.yml").write_text("search-dirs: ['.']")
        (tmp_path / "pyproject.toml").write_text("[tool.taskfile-help]\nsearch-dirs = ['other']")

        config_file = get_config_file()

        assert config_file is not None
        assert isinstance(config_file, TaskfileHelpConfigFile)
        config = config_file.load_config()
        assert config["search-dirs"] == ["."]

    def test_get_config_file_pyproject_toml_fallback(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Get config file when only pyproject.toml exists."""
        monkeypatch.chdir(tmp_path)

        # Create only pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[tool.taskfile-help]\nsearch-dirs = ['other']")

        config_file = get_config_file()

        assert config_file is not None
        assert isinstance(config_file, PyProjectConfigFile)
        config = config_file.load_config()
        assert config["search-dirs"] == ["other"]

    def test_get_config_file_no_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Get config file when no config files exist."""
        monkeypatch.chdir(tmp_path)

        config_file = get_config_file()

        assert config_file is None

    def test_get_config_file_custom_order(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Get config file with custom search order."""
        monkeypatch.chdir(tmp_path)

        # Create both config files
        (tmp_path / "taskfile_help.yml").write_text("search-dirs: ['.']")
        (tmp_path / "pyproject.toml").write_text("[tool.taskfile-help]\nsearch-dirs = ['other']")

        # Search for pyproject.toml first
        config_file = get_config_file(["pyproject.toml", "taskfile_help.yml"])

        assert config_file is not None
        assert isinstance(config_file, PyProjectConfigFile)
        config = config_file.load_config()
        assert config["search-dirs"] == ["other"]

    def test_get_config_file_only_taskfile_help_yml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Get config file when only taskfile_help.yml exists."""
        monkeypatch.chdir(tmp_path)

        # Create only taskfile_help.yml
        (tmp_path / "taskfile_help.yml").write_text("search-dirs: ['.']")

        config_file = get_config_file()

        assert config_file is not None
        assert isinstance(config_file, TaskfileHelpConfigFile)
