"""End-to-end tests for taskfile-help CLI."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from taskfile_help.taskfile_help import main


class TestCLIHelp:
    """Test CLI help output via different invocation methods."""

    def test_main_with_none_argv(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main() called with None (simulates console script entry point)."""
        # Create a simple Taskfile
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
""")
        monkeypatch.chdir(tmp_path)
        
        # Mock sys.argv to simulate console script invocation
        with patch("sys.argv", ["taskfile-help"]):
            with patch("sys.stdout.isatty", return_value=False):
                result = main(None)
        
        assert result == 0

    def test_python_module_help(self) -> None:
        """Test 'python3 -m taskfile_help -h' shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "taskfile_help", "-h"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "Dynamic Taskfile help generator" in result.stdout
        assert "--no-color" in result.stdout
        assert "--search-dirs" in result.stdout
        assert "--json" in result.stdout
        assert "'all'" in result.stdout or "all" in result.stdout  # 'all' namespace mentioned

    def test_console_script_help(self) -> None:
        """Test '.venv/bin/taskfile-help -h' shows help."""
        # Find the taskfile-help script in the virtual environment
        venv_bin = Path(sys.executable).parent
        script_path = venv_bin / "taskfile-help"
        
        if not script_path.exists():
            pytest.skip(f"Console script not found at {script_path}")
        
        result = subprocess.run(
            [str(script_path), "-h"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "Dynamic Taskfile help generator" in result.stdout
        assert "--no-color" in result.stdout
        assert "--search-dirs" in result.stdout
        assert "--json" in result.stdout
        assert "'all'" in result.stdout or "all" in result.stdout  # 'all' namespace mentioned


class TestCLIWithTaskfiles:
    """Test CLI with actual Taskfile content."""

    @pytest.fixture
    def taskfiles_dir(self, tmp_path: Path) -> Path:
        """Create a temporary directory with sample Taskfiles."""
        # Main Taskfile.yaml
        main_taskfile = tmp_path / "Taskfile.yaml"
        main_taskfile.write_text("""version: '3'

tasks:
  # === Build ===
  build:
    desc: Build the project
    cmds:
      - echo "Building..."

  compile:
    desc: Compile sources
    cmds:
      - echo "Compiling..."

  # === Testing ===
  test:
    desc: Run tests
    cmds:
      - echo "Testing..."
""")

        # Dev namespace Taskfile-dev.yml
        dev_taskfile = tmp_path / "Taskfile-dev.yml"
        dev_taskfile.write_text("""version: '3'

tasks:
  # === Development ===
  serve:
    desc: Start development server
    cmds:
      - echo "Serving..."

  watch:
    desc: Watch for changes
    cmds:
      - echo "Watching..."
""")

        # Test namespace Taskfile-test.yaml
        test_taskfile = tmp_path / "Taskfile-test.yaml"
        test_taskfile.write_text("""version: '3'

tasks:
  # === Unit Tests ===
  unit:
    desc: Run unit tests
    cmds:
      - echo "Unit testing..."

  integration:
    desc: Run integration tests
    cmds:
      - echo "Integration testing..."
""")

        return tmp_path

    def test_all_with_color_and_search_dirs(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test 'all' namespace with color enabled using --search-dirs."""
        # Change to a different directory to test --search-dirs
        other_dir = taskfiles_dir.parent / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)
        
        # Mock isatty to enable colors
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["taskfile-help", "all", "--search-dirs", str(taskfiles_dir)])
        
        assert result == 0

    def test_no_color_from_current_dir(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --no-color flag from current directory."""
        monkeypatch.chdir(taskfiles_dir)
        
        # Even with TTY, colors should be disabled
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["taskfile-help", "--no-color"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Verify no ANSI color codes in output
        assert "\x1b[" not in captured.out

    def test_specific_namespace(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test showing specific namespace (test)."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "test"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should show test namespace tasks
        assert "unit" in captured.out
        assert "integration" in captured.out
        assert "Run unit tests" in captured.out
        assert "Run integration tests" in captured.out

    def test_piped_output_no_color(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that piped output (dev | cat) doesn't have color codes."""
        monkeypatch.chdir(taskfiles_dir)
        
        # Simulate piped output by setting isatty to False
        with patch("sys.stdout.isatty", return_value=False):
            # Capture output
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                result = main(["taskfile-help", "dev"])
            
            assert result == 0
            output = output_buffer.getvalue()
            
            # Verify no ANSI color codes
            assert "\x1b[" not in output
            
            # Verify content is present
            assert "serve" in output
            assert "watch" in output
            assert "Start development server" in output

    def test_all_namespace_shows_all_namespaces(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test 'all' namespace shows all namespaces."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "all"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should show tasks from all namespaces
        assert "build" in captured.out  # main
        assert "serve" in captured.out  # dev
        assert "unit" in captured.out   # test

    def test_json_output(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --json output format."""
        monkeypatch.chdir(taskfiles_dir)
        
        result = main(["taskfile-help", "--json"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should be valid JSON
        import json
        output = json.loads(captured.out)
        
        assert "tasks" in output
        assert len(output["tasks"]) > 0
        
        # Verify no color codes in JSON output
        assert "\x1b[" not in captured.out

    def test_verbose_output(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --verbose flag shows search directories."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "--verbose"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Verbose output goes to stderr
        assert "Searching in directories:" in captured.err or "Searching in directories:" in captured.out

    def test_search_dirs_with_multiple_paths(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test --search-dirs with multiple colon-separated paths."""
        # Create two directories with different taskfiles
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        (dir1 / "Taskfile.yaml").write_text("""version: '3'
tasks:
  task1:
    desc: Task from dir1
    cmds: [echo "dir1"]
""")
        
        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        (dir2 / "Taskfile.yaml").write_text("""version: '3'
tasks:
  task2:
    desc: Task from dir2
    cmds: [echo "dir2"]
""")
        
        # Change to a different directory
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)
        
        # First directory in search path should win
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "--search-dirs", f"{dir1}:{dir2}"])
        
        assert result == 0

    def test_nonexistent_namespace(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error when requesting nonexistent namespace."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "nonexistent"])
        
        assert result == 1
        
        captured = capsys.readouterr()
        assert "No Taskfile found" in captured.out or "No Taskfile found" in captured.err

    def test_no_taskfile_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when no Taskfile exists."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help"])
        
        assert result == 1
