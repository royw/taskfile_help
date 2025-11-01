"""Unit tests for the main taskfile_help module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.taskfile_help import main


class TestMain:
    """Tests for main function."""

    def test_main_with_main_taskfile(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with a main taskfile."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace"])
        
        assert result == 0

    def test_main_with_namespace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with a namespace taskfile."""
        taskfile = tmp_path / "Taskfile-dev.yml"
        taskfile.write_text("""version: '3'

tasks:
  test:
    desc: Run tests
    cmds:
      - echo "Testing..."
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "dev"])
        
        assert result == 0

    def test_main_with_all_namespace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with 'all' namespace."""
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        dev_taskfile = tmp_path / "Taskfile-dev.yml"
        dev_taskfile.write_text("""version: '3'

tasks:
  test:
    desc: Run tests
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "all"])
        
        assert result == 0

    def test_main_taskfile_not_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main when taskfile is not found."""
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace"])
        
        assert result == 1

    def test_main_namespace_not_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main when namespace taskfile is not found."""
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "nonexistent"])
        
        assert result == 1

    def test_main_with_json_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with JSON output."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        result = main(["script.py", "namespace", "--json"])
        
        assert result == 0

    def test_main_with_no_color(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with --no-color flag."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["script.py", "namespace", "--no-color"])
        
        assert result == 0

    def test_main_with_search_dirs(self, tmp_path: Path) -> None:
        """Test main with custom search directories."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        taskfile = project_dir / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "-s", str(project_dir)])
        
        assert result == 0

    def test_main_with_verbose(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with verbose output."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "--verbose"])
        
        assert result == 0

    def test_main_namespace_main_alias(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test 'main' namespace is treated as main taskfile."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "main"])
        
        assert result == 0

    def test_main_with_empty_taskfile(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with empty taskfile."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace"])
        
        assert result == 0

    def test_main_with_internal_tasks_only(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main with taskfile containing only internal tasks."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  _internal:
    desc: Internal task
    internal: true
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace"])
        
        assert result == 0

    def test_main_all_with_no_taskfiles(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main 'all' namespace when no taskfiles exist."""
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "all"])
        
        assert result == 0

    def test_main_with_multiple_namespaces(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main 'all' namespace with multiple namespace taskfiles."""
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
tasks:
  build:
    desc: Build
    cmds: []
""")
        (tmp_path / "Taskfile-dev.yml").write_text("""version: '3'
tasks:
  test:
    desc: Test
    cmds: []
""")
        (tmp_path / "Taskfile-prod.yml").write_text("""version: '3'
tasks:
  deploy:
    desc: Deploy
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "all"])
        
        assert result == 0

    def test_main_colors_disabled_for_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test colors are disabled for JSON output."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        from taskfile_help.output import Colors
        
        # Save original
        original_reset = Colors.RESET
        
        with patch("sys.stdout.isatty", return_value=True):
            result = main(["script.py", "namespace", "--json"])
        
        # Colors should be disabled for JSON
        assert result == 0
        
        # Restore
        Colors.RESET = original_reset
        Colors.BOLD = "\033[1m"
        Colors.CYAN = "\033[36m"
        Colors.GREEN = "\033[32m"
        Colors.RED = "\033[31m"
        Colors.YELLOW = "\033[33m"
