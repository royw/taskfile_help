"""Unit tests for the parser module."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from taskfile_help.output import Outputter
from taskfile_help.parser import (
    _extract_description,
    _extract_group_name,
    _extract_task_name,
    _is_internal_task,
    _save_task_if_valid,
    parse_taskfile,
)


class TestExtractGroupName:
    """Tests for _extract_group_name function."""

    def test_valid_group_marker(self) -> None:
        """Test extraction of valid group marker."""
        line = "  # === Build and Release ==="
        result = _extract_group_name(line)
        assert result == "Build and Release"

    def test_group_marker_with_extra_spaces(self) -> None:
        """Test group marker with extra spaces."""
        line = "  #  ===   Testing   ===  "
        result = _extract_group_name(line)
        assert result == "Testing"

    def test_no_group_marker(self) -> None:
        """Test line without group marker."""
        line = "  # This is just a comment"
        result = _extract_group_name(line)
        assert result is None

    def test_empty_line(self) -> None:
        """Test empty line."""
        line = ""
        result = _extract_group_name(line)
        assert result is None

    def test_task_line(self) -> None:
        """Test task definition line (should not match)."""
        line = "  build:"
        result = _extract_group_name(line)
        assert result is None


class TestExtractTaskName:
    """Tests for _extract_task_name function."""

    def test_valid_task_name(self) -> None:
        """Test extraction of valid task name."""
        line = "  build:"
        result = _extract_task_name(line)
        assert result == "build"

    def test_task_with_namespace(self) -> None:
        """Test task name with namespace separator."""
        line = "  help:all:"
        result = _extract_task_name(line)
        assert result == "help:all"

    def test_task_with_hyphens(self) -> None:
        """Test task name with hyphens."""
        line = "  build-docker:"
        result = _extract_task_name(line)
        assert result == "build-docker"

    def test_task_with_underscores(self) -> None:
        """Test task name with underscores."""
        line = "  run_tests:"
        result = _extract_task_name(line)
        assert result == "run_tests"

    def test_invalid_indentation(self) -> None:
        """Test task with wrong indentation."""
        line = "build:"
        result = _extract_task_name(line)
        assert result is None

    def test_desc_line(self) -> None:
        """Test description line (should not match)."""
        line = "    desc: Build the project"
        result = _extract_task_name(line)
        assert result is None


class TestExtractDescription:
    """Tests for _extract_description function."""

    def test_valid_description(self) -> None:
        """Test extraction of valid description."""
        line = "    desc: Build the project"
        result = _extract_description(line)
        assert result == "Build the project"

    def test_description_with_extra_spaces(self) -> None:
        """Test description with extra spaces."""
        line = "    desc:   Run all tests   "
        result = _extract_description(line)
        assert result == "Run all tests"

    def test_empty_description(self) -> None:
        """Test empty description."""
        line = "    desc:"
        result = _extract_description(line)
        assert result is None

    def test_non_desc_line(self) -> None:
        """Test non-description line."""
        line = "    cmds: [echo hello]"
        result = _extract_description(line)
        assert result is None

    def test_task_line(self) -> None:
        """Test task definition line (should not match)."""
        line = "  build:"
        result = _extract_description(line)
        assert result is None


class TestIsInternalTask:
    """Tests for _is_internal_task function."""

    def test_internal_true(self) -> None:
        """Test internal: true flag."""
        line = "    internal: true"
        result = _is_internal_task(line)
        assert result is True

    def test_internal_false(self) -> None:
        """Test internal: false flag."""
        line = "    internal: false"
        result = _is_internal_task(line)
        assert result is False

    def test_non_internal_line(self) -> None:
        """Test non-internal line."""
        line = "    desc: Some description"
        result = _is_internal_task(line)
        assert result is False

    def test_empty_line(self) -> None:
        """Test empty line."""
        line = ""
        result = _is_internal_task(line)
        assert result is False


class TestSaveTaskIfValid:
    """Tests for _save_task_if_valid function."""

    def test_valid_public_task(self) -> None:
        """Test saving a valid public task."""
        tasks: list[tuple[str, str, str]] = []
        _save_task_if_valid(tasks, "Build", "build", "Build the project", False)
        assert len(tasks) == 1
        assert tasks[0] == ("Build", "build", "Build the project")

    def test_internal_task_not_saved(self) -> None:
        """Test that internal tasks are not saved."""
        tasks: list[tuple[str, str, str]] = []
        _save_task_if_valid(tasks, "Build", "build", "Build the project", True)
        assert len(tasks) == 0

    def test_task_without_name_not_saved(self) -> None:
        """Test that tasks without names are not saved."""
        tasks: list[tuple[str, str, str]] = []
        _save_task_if_valid(tasks, "Build", None, "Build the project", False)
        assert len(tasks) == 0

    def test_task_without_description_not_saved(self) -> None:
        """Test that tasks without descriptions are not saved."""
        tasks: list[tuple[str, str, str]] = []
        _save_task_if_valid(tasks, "Build", "build", None, False)
        assert len(tasks) == 0

    def test_multiple_tasks(self) -> None:
        """Test saving multiple tasks."""
        tasks: list[tuple[str, str, str]] = []
        _save_task_if_valid(tasks, "Build", "build", "Build the project", False)
        _save_task_if_valid(tasks, "Test", "test", "Run tests", False)
        assert len(tasks) == 2


class TestParseTaskfile:
    """Tests for parse_taskfile function."""

    def test_parse_simple_taskfile(self, tmp_path: Path) -> None:
        """Test parsing a simple taskfile."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."

  test:
    desc: Run tests
    cmds:
      - echo "Testing..."
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 2
        assert tasks[0] == ("Other", "build", "Build the project")
        assert tasks[1] == ("Other", "test", "Run tests")

    def test_parse_taskfile_with_groups(self, tmp_path: Path) -> None:
        """Test parsing a taskfile with group markers."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  # === Build and Release ===
  build:
    desc: Build the project
    cmds:
      - echo "Building..."

  # === Testing ===
  test:
    desc: Run tests
    cmds:
      - echo "Testing..."
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 2
        assert tasks[0] == ("Build and Release", "build", "Build the project")
        assert tasks[1] == ("Testing", "test", "Run tests")

    def test_parse_taskfile_with_internal_tasks(self, tmp_path: Path) -> None:
        """Test parsing a taskfile with internal tasks."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."

  _internal:
    desc: Internal task
    internal: true
    cmds:
      - echo "Internal..."

  test:
    desc: Run tests
    cmds:
      - echo "Testing..."
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 2
        assert tasks[0] == ("Other", "build", "Build the project")
        assert tasks[1] == ("Other", "test", "Run tests")

    def test_parse_taskfile_without_descriptions(self, tmp_path: Path) -> None:
        """Test parsing a taskfile where tasks lack descriptions."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    cmds:
      - echo "Building..."

  test:
    desc: Run tests
    cmds:
      - echo "Testing..."
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 1
        assert tasks[0] == ("Other", "test", "Run tests")

    def test_parse_nonexistent_file(self, tmp_path: Path) -> None:
        """Test parsing a non-existent file."""
        taskfile = tmp_path / "nonexistent.yml"
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 0
        mock_outputter.output_error.assert_called_once()

    def test_parse_empty_taskfile(self, tmp_path: Path) -> None:
        """Test parsing an empty taskfile."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 0

    def test_parse_taskfile_without_tasks_section(self, tmp_path: Path) -> None:
        """Test parsing a taskfile without tasks section."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

vars:
  VAR: value
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 0

    def test_parse_taskfile_preserves_order(self, tmp_path: Path) -> None:
        """Test that parsing preserves task order."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  zebra:
    desc: Last alphabetically
    cmds: []

  alpha:
    desc: First alphabetically
    cmds: []

  middle:
    desc: Middle alphabetically
    cmds: []
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 3
        assert tasks[0][1] == "zebra"
        assert tasks[1][1] == "alpha"
        assert tasks[2][1] == "middle"

    def test_parse_taskfile_with_unicode(self, tmp_path: Path) -> None:
        """Test parsing a taskfile with unicode characters."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project 🚀
    cmds:
      - echo "Building..."
""", encoding="utf-8")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 1
        assert tasks[0] == ("Other", "build", "Build the project 🚀")
