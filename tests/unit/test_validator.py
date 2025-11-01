"""Unit tests for validator module."""

import pytest

from taskfile_help.output import TextOutputter
from taskfile_help.validator import validate_taskfile


class TestValidateTaskfile:
    """Tests for validate_taskfile function."""

    def test_valid_taskfile_passes(self, capsys):
        """Test valid Taskfile passes validation."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
            "    cmds:\n",
            "      - echo 'building'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is True
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_missing_version_field(self, capsys):
        """Test warning when version field is missing."""
        lines = [
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Missing 'version' field" in captured.err

    def test_wrong_version_string(self, capsys):
        """Test warning when version is '2' instead of '3'."""
        lines = [
            "version: '2'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Invalid version '2', expected '3'" in captured.err

    def test_wrong_version_number(self, capsys):
        """Test warning when version is a number instead of string."""
        lines = [
            "version: 3\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Invalid version '3', expected '3'" in captured.err

    def test_wrong_version_float(self, capsys):
        """Test warning when version is '3.0' instead of '3'."""
        lines = [
            "version: '3.0'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Invalid version '3.0', expected '3'" in captured.err

    def test_missing_tasks_section(self, capsys):
        """Test warning when tasks section is missing."""
        lines = [
            "version: '3'\n",
            "\n",
            "vars:\n",
            "  FOO: bar\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Missing 'tasks' section" in captured.err

    def test_tasks_is_list(self, capsys):
        """Test warning when tasks is a list instead of dictionary."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  - build\n",
            "  - test\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "'tasks' must be a dictionary, got list" in captured.err

    def test_tasks_is_string(self, capsys):
        """Test warning when tasks is a string instead of dictionary."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks: 'not a dict'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "'tasks' must be a dictionary, got str" in captured.err

    def test_invalid_yaml_syntax(self, capsys):
        """Test warning when YAML has syntax errors."""
        lines = [
            "version: '3'\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
            "  invalid indentation\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "is not parseable" in captured.err
        assert "continuing..." in captured.err

    def test_task_is_string(self, capsys):
        """Test warning when task definition is a string instead of dict."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  build: 'should be a dict'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Task 'build' must be a dictionary" in captured.err

    def test_task_desc_is_number(self, capsys):
        """Test warning when task desc is a number instead of string."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: 123\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Task 'build': 'desc' must be a string, got int" in captured.err

    def test_task_internal_is_string(self, capsys):
        """Test warning when task internal is a string instead of boolean."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build\n",
            "    internal: 'yes'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Task 'build': 'internal' must be a boolean, got str" in captured.err

    def test_task_cmds_is_dict(self, capsys):
        """Test warning when task cmds is a dict instead of list or string."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build\n",
            "    cmds:\n",
            "      key: value\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Task 'build': 'cmds' must be a list or string, got dict" in captured.err

    def test_task_deps_is_string(self, capsys):
        """Test warning when task deps is a string instead of list."""
        lines = [
            "version: '3'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build\n",
            "    deps: 'not-a-list'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Task 'build': 'deps' must be a list, got str" in captured.err

    def test_multiple_validation_errors(self, capsys):
        """Test multiple validation errors are reported."""
        lines = [
            "version: '2'\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: 123\n",
            "    internal: 'yes'\n",
            "  test: 'not a dict'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Invalid version '2', expected '3'" in captured.err
        assert "Task 'build': 'desc' must be a string, got int" in captured.err
        assert "Task 'build': 'internal' must be a boolean, got str" in captured.err
        assert "Task 'test' must be a dictionary" in captured.err

    def test_root_is_list(self, capsys):
        """Test warning when root is a list instead of dictionary."""
        lines = [
            "- version: '3'\n",
            "- tasks:\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Root must be a dictionary, got list" in captured.err

    def test_valid_taskfile_with_optional_fields(self, capsys):
        """Test valid optional fields produce no warnings."""
        lines = [
            "version: '3'\n",
            "\n",
            "vars:\n",
            "  FOO: bar\n",
            "\n",
            "tasks:\n",
            "  build:\n",
            "    desc: Build the project\n",
            "    internal: true\n",
            "    cmds:\n",
            "      - echo 'building'\n",
            "    deps:\n",
            "      - clean\n",
            "  clean:\n",
            "    desc: Clean\n",
            "    cmds: echo 'cleaning'\n",
        ]
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is True
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_empty_file(self, capsys):
        """Test warning when file is empty."""
        lines = []
        outputter = TextOutputter()
        
        result = validate_taskfile(lines, outputter)
        
        assert result is False
        captured = capsys.readouterr()
        assert "Root must be a dictionary, got NoneType" in captured.err
