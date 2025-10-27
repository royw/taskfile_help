"""Unit tests for the output module."""

from io import StringIO
from unittest.mock import Mock

import pytest

from taskfile_help.output import Colors, JsonOutputter, TextOutputter


class TestColors:
    """Tests for Colors class."""

    def test_colors_enabled_by_default(self) -> None:
        """Test that colors are enabled by default."""
        assert Colors.RESET == "\033[0m"
        assert Colors.BOLD == "\033[1m"
        assert Colors.CYAN == "\033[36m"
        assert Colors.GREEN == "\033[32m"
        assert Colors.RED == "\033[31m"
        assert Colors.YELLOW == "\033[33m"

    def test_disable_colors(self) -> None:
        """Test disabling colors."""
        # Save original values
        original_reset = Colors.RESET
        
        Colors.disable()
        
        assert Colors.RESET == ""
        assert Colors.BOLD == ""
        assert Colors.CYAN == ""
        assert Colors.GREEN == ""
        assert Colors.RED == ""
        assert Colors.YELLOW == ""
        
        # Restore for other tests
        Colors.RESET = original_reset
        Colors.BOLD = "\033[1m"
        Colors.CYAN = "\033[36m"
        Colors.GREEN = "\033[32m"
        Colors.RED = "\033[31m"
        Colors.YELLOW = "\033[33m"


class TestTextOutputter:
    """Tests for TextOutputter class."""

    def test_output_single_with_tasks(self) -> None:
        """Test outputting tasks for a single namespace."""
        outputter = TextOutputter()
        tasks = [
            ("Build", "build", "Build the project"),
            ("Build", "clean", "Clean build artifacts"),
            ("Test", "test", "Run tests"),
        ]
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_single("dev", tasks, capture_output)
        
        output = "\n".join(output_lines)
        assert "DEV Task Commands:" in output
        assert "Build:" in output
        assert "build" in output
        assert "clean" in output
        assert "Test:" in output
        assert "test" in output

    def test_output_single_no_tasks(self) -> None:
        """Test outputting when no tasks exist."""
        outputter = TextOutputter()
        tasks: list[tuple[str, str, str]] = []
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_single("dev", tasks, capture_output)
        
        output = "\n".join(output_lines)
        assert "No public tasks found" in output

    def test_output_single_main_namespace(self) -> None:
        """Test outputting tasks for main namespace (empty string)."""
        outputter = TextOutputter()
        tasks = [("Build", "build", "Build the project")]
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_single("", tasks, capture_output)
        
        output = "\n".join(output_lines)
        assert "Task Commands:" in output
        assert "DEV" not in output

    def test_output_all(self) -> None:
        """Test outputting all taskfiles."""
        outputter = TextOutputter()
        taskfiles = [
            ("", [("Build", "build", "Build the project")]),
            ("dev", [("Test", "test", "Run tests")]),
        ]
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_all(taskfiles, capture_output)
        
        output = "\n".join(output_lines)
        assert "Main Taskfile" in output
        assert "DEV Taskfile" in output

    def test_output_heading(self) -> None:
        """Test outputting a heading."""
        outputter = TextOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_heading("Test Heading", capture_output)
        
        assert len(output_lines) == 1
        assert "Test Heading" in output_lines[0]

    def test_output_message(self) -> None:
        """Test outputting a message."""
        outputter = TextOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_message("Test message", capture_output)
        
        assert output_lines == ["Test message"]

    def test_output_error(self) -> None:
        """Test outputting an error message."""
        outputter = TextOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str, **kwargs: object) -> None:
            output_lines.append(text)
        
        outputter.output_error("Test error", capture_output)
        
        assert len(output_lines) == 1
        assert "Error:" in output_lines[0]
        assert "Test error" in output_lines[0]

    def test_output_warning(self) -> None:
        """Test outputting a warning message."""
        outputter = TextOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str, **kwargs: object) -> None:
            output_lines.append(text)
        
        outputter.output_warning("Test warning", capture_output)
        
        assert len(output_lines) == 1
        assert "Warning:" in output_lines[0]
        assert "Test warning" in output_lines[0]


class TestJsonOutputter:
    """Tests for JsonOutputter class."""

    def test_output_single_with_tasks(self) -> None:
        """Test outputting tasks in JSON format."""
        outputter = JsonOutputter()
        tasks = [
            ("Build", "build", "Build the project"),
            ("Test", "test", "Run tests"),
        ]
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_single("dev", tasks, capture_output)
        
        import json
        output = json.loads("\n".join(output_lines))
        
        assert output["namespace"] == "dev"
        assert len(output["tasks"]) == 2
        assert output["tasks"][0]["name"] == "build"
        assert output["tasks"][0]["group"] == "Build"
        assert output["tasks"][0]["full_name"] == "dev:build"
        assert output["tasks"][0]["description"] == "Build the project"

    def test_output_single_main_namespace(self) -> None:
        """Test outputting tasks for main namespace in JSON."""
        outputter = JsonOutputter()
        tasks = [("Build", "build", "Build the project")]
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_single("", tasks, capture_output)
        
        import json
        output = json.loads("\n".join(output_lines))
        
        assert output["namespace"] == ""
        assert output["tasks"][0]["full_name"] == "build"

    def test_output_all(self) -> None:
        """Test outputting all taskfiles in JSON format."""
        outputter = JsonOutputter()
        taskfiles = [
            ("", [("Build", "build", "Build the project")]),
            ("dev", [("Test", "test", "Run tests")]),
        ]
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_all(taskfiles, capture_output)
        
        import json
        output = json.loads("\n".join(output_lines))
        
        assert len(output["taskfiles"]) == 2
        assert output["taskfiles"][0]["namespace"] == ""
        assert output["taskfiles"][1]["namespace"] == "dev"

    def test_output_heading(self) -> None:
        """Test outputting a heading in JSON format."""
        outputter = JsonOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_heading("Test Heading", capture_output)
        
        assert output_lines == ["Test Heading"]

    def test_output_message(self) -> None:
        """Test outputting a message in JSON format."""
        outputter = JsonOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_message("Test message", capture_output)
        
        assert output_lines == ["Test message"]

    def test_output_error(self) -> None:
        """Test outputting an error in JSON format."""
        outputter = JsonOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str, **kwargs: object) -> None:
            output_lines.append(text)
        
        outputter.output_error("Test error", capture_output)
        
        import json
        output = json.loads(output_lines[0])
        assert output["error"] == "Test error"

    def test_output_warning(self) -> None:
        """Test outputting a warning in JSON format."""
        outputter = JsonOutputter()
        
        output_lines: list[str] = []
        def capture_output(text: str, **kwargs: object) -> None:
            output_lines.append(text)
        
        outputter.output_warning("Test warning", capture_output)
        
        import json
        output = json.loads(output_lines[0])
        assert output["warning"] == "Test warning"

    def test_output_empty_tasks(self) -> None:
        """Test outputting empty task list in JSON."""
        outputter = JsonOutputter()
        tasks: list[tuple[str, str, str]] = []
        
        output_lines: list[str] = []
        def capture_output(text: str) -> None:
            output_lines.append(text)
        
        outputter.output_single("dev", tasks, capture_output)
        
        import json
        output = json.loads("\n".join(output_lines))
        
        assert output["namespace"] == "dev"
        assert output["tasks"] == []
