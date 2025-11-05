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
        """Test main() accepts None as argv parameter."""
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
        with patch("sys.argv", ["taskfile-help", "namespace"]):
            with patch("sys.stdout.isatty", return_value=False):
                result = main(None)
        
        assert result == 0

    def test_python_module_help(self) -> None:
        """Test CLI displays help when invoked as Python module."""
        result = subprocess.run(
            [sys.executable, "-m", "taskfile_help", "-h"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "Dynamic Taskfile help generator" in result.stdout
        assert "namespace" in result.stdout
        assert "search" in result.stdout

    def test_console_script_help(self) -> None:
        """Test CLI displays help when invoked as console script."""
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
        assert "namespace" in result.stdout
        assert "search" in result.stdout


class TestCLIWithTaskfiles:
    """Test CLI with actual Taskfile content."""

    @pytest.fixture
    def taskfiles_dir(self, tmp_path: Path) -> Path:
        """Create a temporary directory with sample Taskfiles."""
        # Main Taskfile.yaml
        main_taskfile = tmp_path / "Taskfile.yaml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
  test:
    taskfile: ./Taskfile-test.yaml
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

    def test_search_dirs_option(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --search-dirs option locates Taskfiles in specified directory."""
        # Change to a different directory to test --search-dirs
        other_dir = taskfiles_dir.parent / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "--search-dirs", str(taskfiles_dir)])
        
        assert result == 0
        captured = capsys.readouterr()
        # Verify tasks from the specified directory are found
        assert "build" in captured.out

    def test_all_namespace_with_color(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test 'all' meta-namespace works with color output enabled."""
        monkeypatch.chdir(taskfiles_dir)
        
        # Mock isatty to enable colors
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["taskfile-help", "namespace", "all"])
        
        assert result == 0

    def test_no_color_from_current_dir(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --no-color flag disables ANSI color codes in output."""
        monkeypatch.chdir(taskfiles_dir)
        
        # Even with TTY, colors should be disabled
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["taskfile-help", "namespace", "--no-color"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Verify no ANSI color codes in output
        assert "\x1b[" not in captured.out

    def test_specific_namespace(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test namespace command displays tasks from specified namespace."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "test"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should show test namespace tasks
        assert "unit" in captured.out
        assert "integration" in captured.out
        assert "Run unit tests" in captured.out
        assert "Run integration tests" in captured.out

    def test_multiple_specific_namespaces(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test namespace command displays tasks from multiple specified namespaces."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "test", "dev"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should show test namespace tasks
        assert "unit" in captured.out
        assert "integration" in captured.out
        assert "Run unit tests" in captured.out
        # Should also show dev namespace tasks
        assert "serve" in captured.out
        assert "watch" in captured.out
        assert "Start development server" in captured.out

    def test_piped_output_no_color(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test piped output automatically disables ANSI color codes."""
        monkeypatch.chdir(taskfiles_dir)
        
        # Simulate piped output by setting isatty to False
        with patch("sys.stdout.isatty", return_value=False):
            # Capture output
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                result = main(["taskfile-help", "namespace", "dev"])
            
            assert result == 0
            output = output_buffer.getvalue()
            
            # Verify no ANSI color codes
            assert "\x1b[" not in output
            
            # Verify content is present
            assert "serve" in output
            assert "watch" in output
            assert "Start development server" in output

    def test_all_namespace_shows_all_namespaces(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test 'all' meta-namespace displays tasks from all namespaces."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "all"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should show tasks from all namespaces
        assert "build" in captured.out  # main
        assert "serve" in captured.out  # dev
        assert "unit" in captured.out   # test

    def test_json_output(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --json flag outputs tasks in JSON format."""
        monkeypatch.chdir(taskfiles_dir)
        
        result = main(["taskfile-help", "namespace", "--json"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Should be valid JSON
        import json
        output = json.loads(captured.out)
        
        assert "tasks" in output
        assert len(output["tasks"]) > 0

    def test_json_output_no_color_codes(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test JSON output never contains ANSI color codes."""
        monkeypatch.chdir(taskfiles_dir)
        
        # Even with TTY, JSON should not have color codes
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["taskfile-help", "namespace", "--json"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Verify no color codes in JSON output
        assert "\x1b[" not in captured.out

    def test_verbose_output(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --verbose flag displays search directory information."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "--verbose"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        # Verbose output goes to stderr
        assert "Searching in directories:" in captured.err or "Searching in directories:" in captured.out

    def test_search_dirs_with_multiple_paths(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test --search-dirs accepts multiple colon-separated directory paths."""
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
            result = main(["taskfile-help", "namespace", "--search-dirs", f"{dir1}:{dir2}"])
        
        assert result == 0

    def test_question_mark_lists_namespaces(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test '?' meta-namespace displays list of available namespaces."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "?"])
        
        assert result == 0
        
        captured = capsys.readouterr()
        output = captured.out + captured.err
        # Should list available namespaces
        assert "Available namespaces:" in output
        assert "dev" in output
        assert "test" in output

    def test_nonexistent_namespace(self, taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test requesting nonexistent namespace returns error with suggestions."""
        monkeypatch.chdir(taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace", "nonexistent"])
        
        assert result == 1
        
        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "No Taskfile found" in output
        # Should suggest available namespaces
        assert "Available namespaces:" in output
        assert "dev" in output
        assert "test" in output

    def test_no_taskfile_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CLI returns error when no Taskfile is found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace"])
        
        assert result == 1


class TestCLIValidation:
    """Test CLI validation warnings."""

    def test_invalid_version_shows_warning(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """Test invalid Taskfile version displays warning but continues processing."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '2'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace"])
        
        assert result == 0  # Should still succeed
        captured = capsys.readouterr()
        assert "Invalid version '2', expected '3'" in captured.err
        assert "build" in captured.out  # Task should still be shown

    def test_missing_version_shows_warning(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """Test missing Taskfile version displays warning but continues processing."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace"])
        
        assert result == 0  # Should still succeed
        captured = capsys.readouterr()
        assert "Missing 'version' field" in captured.err
        assert "build" in captured.out  # Task should still be shown

    def test_invalid_task_structure_shows_warning(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """Test invalid task structure displays warnings but continues processing."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: 123
    internal: "not a boolean"
    cmds:
      - echo "Building..."
  test: "should be a dict"
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace"])
        
        assert result == 0  # Should still succeed
        captured = capsys.readouterr()
        assert "Task 'build': 'desc' must be a string, got int" in captured.err
        assert "Task 'build': 'internal' must be a boolean, got str" in captured.err
        assert "Task 'test' must be a dictionary" in captured.err
        assert "build" in captured.out  # Valid task should still be shown

    def test_valid_taskfile_no_warnings(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """Test valid Taskfile produces no validation warnings."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
  test:
    desc: Run tests
    internal: true
    deps:
      - build
    cmds:
      - echo "Testing..."
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Warning:" not in captured.err
        assert "build" in captured.out
        assert "test" not in captured.out  # Internal task should not be shown

    def test_invalid_yaml_syntax_shows_warning(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """Test invalid YAML syntax displays warning but continues processing."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'
tasks:
  build:
    desc: Build
  invalid indentation
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "namespace"])
        
        # Should still succeed (non-fatal)
        assert result == 0
        captured = capsys.readouterr()
        assert "is not parseable" in captured.err
        assert "continuing..." in captured.err


class TestCLICompletion:
    """Test CLI completion functionality."""

    def test_completion_bash(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --completion bash outputs bash shell completion script."""
        result = main(["taskfile-help", "namespace", "--completion", "bash"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "_taskfile_help_completion()" in captured.out
        assert "complete -F _taskfile_help_completion taskfile-help" in captured.out
        assert "taskfile-help --complete" in captured.out

    def test_completion_zsh(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --completion zsh outputs zsh shell completion script."""
        result = main(["taskfile-help", "namespace", "--completion", "zsh"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "#compdef taskfile-help" in captured.out
        assert "_taskfile_help()" in captured.out
        assert "taskfile-help --complete" in captured.out

    def test_completion_fish(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --completion fish outputs fish shell completion script."""
        result = main(["taskfile-help", "namespace", "--completion", "fish"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "complete -c taskfile-help" in captured.out
        assert "taskfile-help --complete" in captured.out

    def test_completion_unknown_shell(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --completion with unsupported shell returns error."""
        result = main(["taskfile-help", "namespace", "--completion", "powershell"])
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown shell" in captured.err

    def test_complete_namespaces(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --complete outputs list of available namespaces."""
        # Create taskfiles
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
  test:
    taskfile: ./Taskfile-test.yml
tasks:
  build:
    desc: Build
""")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks:\n  serve:\n    desc: Serve\n")
        (tmp_path / "Taskfile-test.yml").write_text("version: '3'\ntasks:\n  unit:\n    desc: Unit\n")
        
        monkeypatch.chdir(tmp_path)
        
        result = main(["taskfile-help", "namespace", "--complete", ""])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "main" in captured.out
        assert "all" in captured.out
        assert "dev" in captured.out
        assert "test" in captured.out

    def test_complete_partial_namespace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --complete filters namespaces by partial prefix match."""
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
  deploy:
    taskfile: ./Taskfile-deploy.yml
  test:
    taskfile: ./Taskfile-test.yml
""")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\n")
        (tmp_path / "Taskfile-deploy.yml").write_text("version: '3'\n")
        (tmp_path / "Taskfile-test.yml").write_text("version: '3'\n")
        
        monkeypatch.chdir(tmp_path)
        
        result = main(["taskfile-help", "namespace", "--complete", "de"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "dev" in captured.out
        assert "deploy" in captured.out
        assert "test" not in captured.out

    def test_complete_task_names(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --complete outputs task names for namespace:task completion."""
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
""")
        (tmp_path / "Taskfile-dev.yml").write_text("""version: '3'
tasks:
  build:
    desc: Build
  test:
    desc: Test
  deploy:
    desc: Deploy
""")
        
        monkeypatch.chdir(tmp_path)
        
        result = main(["taskfile-help", "namespace", "--complete", "dev:"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "dev:build" in captured.out
        assert "dev:test" in captured.out
        assert "dev:deploy" in captured.out

    def test_complete_partial_task_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --complete filters task names by partial prefix match."""
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
""")
        (tmp_path / "Taskfile-dev.yml").write_text("""version: '3'
tasks:
  build:
    desc: Build
  build-all:
    desc: Build all
  test:
    desc: Test
""")
        
        monkeypatch.chdir(tmp_path)
        
        result = main(["taskfile-help", "namespace", "--complete", "dev:build"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "dev:build" in captured.out
        assert "dev:build-all" in captured.out
        assert "dev:test" not in captured.out

    def test_install_completion_bash(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --install-completion bash installs completion script to user directory."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = main(["taskfile-help", "namespace", "--install-completion", "bash"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Completion script installed" in captured.out
        assert ".bash_completion.d/taskfile-help" in captured.out
        assert (tmp_path / ".bash_completion.d" / "taskfile-help").exists()

    def test_install_completion_auto_detect(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --install-completion auto-detects shell from SHELL environment variable."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch.dict("os.environ", {"SHELL": "/bin/bash"}):
                result = main(["taskfile-help", "namespace", "--install-completion"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Completion script installed" in captured.out
        assert (tmp_path / ".bash_completion.d" / "taskfile-help").exists()


class TestCLISearch:
    """Test CLI search command functionality."""

    @pytest.fixture
    def search_taskfiles_dir(self, tmp_path: Path) -> Path:
        """Create a temporary directory with sample Taskfiles for search testing."""
        # Main Taskfile.yaml
        main_taskfile = tmp_path / "Taskfile.yaml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
  format:
    taskfile: ./Taskfile-format.yml
tasks:
  # === Build ===
  build:
    desc: Build the project
    cmds:
      - echo "Building..."

  build-all:
    desc: Build all components
    cmds:
      - echo "Building all..."

  # === Testing ===
  test:
    desc: Run tests
    cmds:
      - echo "Testing..."

  test-unit:
    desc: Run unit tests
    cmds:
      - echo "Unit testing..."
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

  # === Testing ===
  test-integration:
    desc: Run integration tests
    cmds:
      - echo "Integration testing..."
""")

        # Format namespace Taskfile-format.yml
        format_taskfile = tmp_path / "Taskfile-format.yml"
        format_taskfile.write_text("""version: '3'

tasks:
  # === Code Formatting ===
  format-all:
    desc: Format all code
    cmds:
      - echo "Formatting..."

  format-check:
    desc: Check code formatting
    cmds:
      - echo "Checking format..."

  # === Linting ===
  lint:
    desc: Run linter
    cmds:
      - echo "Linting..."

  lint-fix:
    desc: Fix linting issues
    cmds:
      - echo "Fixing lint..."
""")

        return tmp_path

    def test_search_pattern_basic(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test pattern search matches task names containing the pattern."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "test"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should find tasks with "test" in name
        assert "test" in captured.out.lower()
        assert "test-unit" in captured.out
        assert "test-integration" in captured.out
        # Should not find unrelated tasks
        assert "serve" not in captured.out
        assert "format" not in captured.out

    def test_search_pattern_case_insensitive(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test pattern search performs case-insensitive matching."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "BUILD"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        assert "build" in captured.out.lower()
        assert "build-all" in captured.out

    def test_search_regex_basic(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --regex flag enables regular expression pattern matching."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "--regex", "test"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should find tasks with "test" anywhere in combined text
        assert "test" in captured.out.lower()
        assert "test-unit" in captured.out or "unit" in captured.out

    def test_search_regex_end_anchor(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test regex search supports word boundary anchors."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "--regex", r"\ball\b"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should find tasks with "all" as a complete word
        assert "all" in captured.out.lower()
        assert "build-all" in captured.out or "format-all" in captured.out

    def test_search_combined_filters(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test combining pattern and --regex applies AND logic to filters."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "check", "--regex", "^format"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should find tasks matching both filters (starts with format AND contains check)
        assert "format-check" in captured.out
        # Should not find tasks that don't match both
        assert "format-all" not in captured.out
        assert "lint" not in captured.out

    def test_search_no_results(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search displays appropriate message when no tasks match."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "nonexistent"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        assert "No tasks found matching search criteria" in captured.out

    def test_search_missing_pattern_error(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search command requires at least one search filter."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search"])
        
        assert result == 1  # Returns error code 1
        captured = capsys.readouterr()
        
        # Should show error message about needing at least one filter
        assert "At least one search filter" in captured.err or "required" in captured.err.lower()

    def test_search_json_output(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --json flag outputs search results in JSON format."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        result = main(["taskfile-help", "search", "test", "--json"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should be valid JSON
        import json
        output = json.loads(captured.out)
        
        assert "results" in output
        assert len(output["results"]) > 0

    def test_search_json_structure(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search JSON output contains required result fields."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        result = main(["taskfile-help", "search", "test", "--json"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        import json
        output = json.loads(captured.out)
        
        # Check structure of results
        first_result = output["results"][0]
        assert "namespace" in first_result
        assert "group" in first_result
        assert "name" in first_result
        assert "full_name" in first_result
        assert "description" in first_result
        assert "match_type" in first_result

    def test_search_with_no_color(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --no-color flag disables ANSI color codes in search output."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["taskfile-help", "search", "build", "--no-color"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Verify no ANSI color codes
        assert "\x1b[" not in captured.out
        assert "build" in captured.out

    def test_search_with_verbose(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --verbose flag displays search directory information."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "test", "--verbose"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Verbose output should show search directories
        assert "Searching in directories:" in captured.err or "Searching in directories:" in captured.out

    def test_search_with_search_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search command respects --search-dirs option."""
        # Create taskfiles in a subdirectory
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "Taskfile.yml").write_text("""version: '3'
tasks:
  deploy:
    desc: Deploy application
    cmds: [echo "Deploying..."]
""")
        
        # Change to different directory
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "deploy", "--search-dirs", str(project_dir)])
        
        assert result == 0
        captured = capsys.readouterr()
        
        assert "deploy" in captured.out

    def test_search_namespace_match(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search displays all tasks when pattern matches namespace name."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "format"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should show FORMAT namespace header
        assert "FORMAT" in captured.out.upper() or "format" in captured.out.lower()
        # Should show all tasks from format namespace
        assert "format-all" in captured.out
        assert "format-check" in captured.out
        assert "lint" in captured.out
        assert "lint-fix" in captured.out

    def test_search_group_match(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search displays all tasks when pattern matches group name."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "linting"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should show Linting group
        assert "Linting" in captured.out or "linting" in captured.out.lower()
        # Should show tasks from Linting group
        assert "lint" in captured.out
        assert "lint-fix" in captured.out

    def test_search_invalid_regex(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search handles invalid regex patterns gracefully."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "test", "--regex", "[invalid("])
        
        # Should handle gracefully - either error or no results
        assert result in [0, 1]
        captured = capsys.readouterr()
        
        # Should either show error or no results
        output = captured.out + captured.err
        assert "Invalid regex" in output or "No tasks found" in output or "error" in output.lower()

    def test_search_multiple_namespaces(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search returns matching tasks across all namespaces."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "test"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Should show results from both Main and DEV namespaces
        assert "Main" in captured.out or "MAIN" in captured.out
        assert "DEV" in captured.out or "dev" in captured.out
        assert "test" in captured.out
        assert "test-unit" in captured.out
        assert "test-integration" in captured.out

    def test_search_description_match(self, search_taskfiles_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search matches text in task descriptions."""
        monkeypatch.chdir(search_taskfiles_dir)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["taskfile-help", "search", "server"])
        
        assert result == 0
        captured = capsys.readouterr()
        
        # "server" is in description, so it SHOULD be found
        # (new behavior: search includes descriptions)
        assert "serve" in captured.out or "server" in captured.out.lower()

    def test_namespace_command_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test namespace command help displays meta-namespace documentation."""
        with pytest.raises(SystemExit) as exc_info:
            main(["taskfile-help", "namespace", "--help"])
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        
        assert "Meta-namespaces:" in captured.out
        assert "main" in captured.out
        assert "all" in captured.out
        assert "?" in captured.out

    def test_search_command_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test search command help displays filter options and examples."""
        with pytest.raises(SystemExit) as exc_info:
            main(["taskfile-help", "search", "--help"])
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        
        assert "pattern" in captured.out  # positional argument
        assert "--regex" in captured.out
        assert "Search filters:" in captured.out
        assert "Examples:" in captured.out


class TestCLIInvalidCommand:
    """Test CLI error handling for invalid commands."""

    def test_invalid_command_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error message for invalid command."""
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
        
        # Manually create a Config with an invalid command
        # We need to bypass argparse which would catch this earlier
        from taskfile_help.config import Config
        from taskfile_help.output import create_outputter
        
        # Create a mock config with invalid command
        config = Config(["taskfile-help", "namespace"])
        config.args.command = "invalid_command"  # Force invalid command
        
        outputter = create_outputter(config)
        
        from taskfile_help.taskfile_help import _handle_command
        result = _handle_command(config, outputter)
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Invalid command 'invalid_command'" in captured.err
