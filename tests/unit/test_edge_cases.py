"""Tests for edge cases and error paths."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.config import Config, _load_pyproject_config
from taskfile_help.output import Outputter, TextOutputter
from taskfile_help.parser import parse_taskfile
from taskfile_help.taskfile_help import main


class TestParserEdgeCases:
    """Edge cases for parser module."""

    def test_parse_file_with_encoding_error(self, tmp_path: Path) -> None:
        """Test parsing a file with invalid encoding."""
        taskfile = tmp_path / "Taskfile.yml"
        # Write binary data that's not valid UTF-8
        taskfile.write_bytes(b'\x80\x81\x82\x83')
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 0
        mock_outputter.output_error.assert_called_once()

    @pytest.mark.skipif(
        not hasattr(Path, "chmod"),
        reason="chmod not available on this platform"
    )
    def test_parse_file_permission_denied(self, tmp_path: Path) -> None:
        """Test parsing a file without read permissions."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        try:
            taskfile.chmod(0o000)  # Remove all permissions
            
            mock_outputter = Mock(spec=Outputter)
            tasks = parse_taskfile(taskfile, "", mock_outputter)
            
            assert len(tasks) == 0
            mock_outputter.output_error.assert_called_once()
        finally:
            # Cleanup - restore permissions
            taskfile.chmod(0o644)

    def test_parse_taskfile_multiple_desc_lines(self, tmp_path: Path) -> None:
        """Test task with multiple desc lines (last one wins)."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: First description
    desc: Second description
    cmds: []
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        assert len(tasks) == 1
        # Last description should win
        assert tasks[0][2] == "Second description"

    def test_parse_taskfile_desc_before_task(self, tmp_path: Path) -> None:
        """Test desc appearing before any task definition."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
    desc: Orphaned description
  build:
    desc: Build the project
    cmds: []
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        # Orphaned desc should be ignored
        assert len(tasks) == 1
        assert tasks[0] == ("Other", "build", "Build the project")

    def test_parse_taskfile_internal_before_desc(self, tmp_path: Path) -> None:
        """Test internal flag appearing before desc."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    internal: true
    desc: Build the project
    cmds: []
""")
        mock_outputter = Mock(spec=Outputter)
        tasks = parse_taskfile(taskfile, "", mock_outputter)
        
        # Task should still be marked internal
        assert len(tasks) == 0


class TestConfigEdgeCases:
    """Edge cases for config module."""

    @pytest.mark.skipif(
        not hasattr(Path, "chmod"),
        reason="chmod not available on this platform"
    )
    def test_load_config_permission_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config when pyproject.toml is not readable."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.taskfile-help]\nsearch-dirs = ['.']")
        
        try:
            pyproject.chmod(0o000)
            monkeypatch.chdir(tmp_path)
            
            config = _load_pyproject_config()
            
            # Should silently return empty dict
            assert config == {}
        finally:
            # Cleanup
            pyproject.chmod(0o644)

    def test_config_nonexistent_search_dir(self, tmp_path: Path) -> None:
        """Test config with non-existent search directory."""
        nonexistent = tmp_path / "does_not_exist"
        
        # Should not crash, just use the path
        config = Config(["script.py", "-s", str(nonexistent)])
        
        assert nonexistent in config.discovery.search_dirs

    def test_config_search_dirs_with_spaces(self, tmp_path: Path) -> None:
        """Test search dirs with spaces in path names."""
        dir_with_spaces = tmp_path / "dir with spaces"
        dir_with_spaces.mkdir()
        
        config = Config(["script.py", "-s", str(dir_with_spaces)])
        
        assert dir_with_spaces in config.discovery.search_dirs


class TestOutputEdgeCases:
    """Edge cases for output module."""

    def test_text_outputter_error_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error message output."""
        outputter = TextOutputter()
        outputter.output_error("Test error message")
        
        captured = capsys.readouterr()
        assert "Error: Test error message" in captured.err

    def test_text_outputter_warning_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test warning message output."""
        outputter = TextOutputter()
        outputter.output_warning("Test warning message")
        
        captured = capsys.readouterr()
        assert "Warning: Test warning message" in captured.err

    def test_text_outputter_heading_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test heading message output."""
        outputter = TextOutputter()
        outputter.output_heading("Test Heading")
        
        captured = capsys.readouterr()
        assert "Test Heading" in captured.out

    def test_text_outputter_plain_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test plain message output."""
        outputter = TextOutputter()
        outputter.output_message("Test message")
        
        captured = capsys.readouterr()
        assert "Test message" in captured.out


class TestMainEdgeCases:
    """Edge cases for main function."""

    def test_main_all_namespace_shows_everything(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test 'all' namespace shows all taskfiles."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'
tasks:
  build:
    desc: Build
    cmds: []
""")
        dev_taskfile = tmp_path / "Taskfile-dev.yml"
        dev_taskfile.write_text("""version: '3'
tasks:
  serve:
    desc: Serve
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            # 'all' namespace shows all taskfiles
            result = main(["script.py", "all"])
        
        assert result == 0

    def test_main_verbose_with_json_suppressed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that verbose output is suppressed with JSON."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'
tasks:
  build:
    desc: Build
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        result = main(["script.py", "--verbose", "--json"])
        
        assert result == 0
        captured = capsys.readouterr()
        # Verbose output should not appear with JSON
        assert "Searching in directories:" not in captured.err
        # Should have JSON output
        assert "{" in captured.out

    def test_main_empty_taskfile_with_all(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test 'all' namespace with empty taskfile."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'
tasks:
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "all"])
        
        assert result == 0
        # Should not crash, just show no tasks

    def test_main_colors_disabled_for_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that colors are disabled for JSON output even with TTY."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'
tasks:
  build:
    desc: Build
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["script.py", "--json"])
        
        assert result == 0
        captured = capsys.readouterr()
        # No ANSI color codes in JSON output
        assert "\x1b[" not in captured.out
