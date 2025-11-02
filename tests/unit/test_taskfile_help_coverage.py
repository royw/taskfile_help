"""Additional unit tests for taskfile_help module to improve coverage."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.taskfile_help import main


class TestCompletionFeatures:
    """Tests for completion-related features."""

    def test_completion_script_generation_bash(self, capsys: pytest.CaptureFixture) -> None:
        """Test generating bash completion script."""
        result = main(["script.py", "namespace", "--completion", "bash"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "bash" in captured.out or "_taskfile_help" in captured.out

    def test_completion_script_generation_zsh(self, capsys: pytest.CaptureFixture) -> None:
        """Test generating zsh completion script."""
        result = main(["script.py", "namespace", "--completion", "zsh"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_completion_script_generation_fish(self, capsys: pytest.CaptureFixture) -> None:
        """Test generating fish completion script."""
        result = main(["script.py", "namespace", "--completion", "fish"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_completion_script_generation_unknown_shell(self, capsys: pytest.CaptureFixture) -> None:
        """Test generating completion script for unknown shell."""
        result = main(["script.py", "namespace", "--completion", "unknown"])
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown shell" in captured.err
        assert "Supported shells" in captured.err

    def test_completion_helper(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
        """Test completion helper for shell callbacks."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
  test:
    desc: Run tests
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        result = main(["script.py", "namespace", "--complete", "bu"])
        
        assert result == 0
        captured = capsys.readouterr()
        # Should suggest completions
        assert len(captured.out) > 0

    def test_completion_installation_auto(self, capsys: pytest.CaptureFixture) -> None:
        """Test completion installation with auto-detection."""
        with patch("taskfile_help.taskfile_help.install_completion") as mock_install:
            mock_install.return_value = (True, "Installation successful")
            
            result = main(["script.py", "namespace", "--install-completion"])
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Installation successful" in captured.out
            mock_install.assert_called_once_with(None)

    def test_completion_installation_specific_shell(self, capsys: pytest.CaptureFixture) -> None:
        """Test completion installation for specific shell."""
        with patch("taskfile_help.taskfile_help.install_completion") as mock_install:
            mock_install.return_value = (True, "Installed for bash")
            
            result = main(["script.py", "namespace", "--install-completion", "bash"])
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Installed for bash" in captured.out
            mock_install.assert_called_once_with("bash")

    def test_completion_installation_failure(self, capsys: pytest.CaptureFixture) -> None:
        """Test completion installation failure."""
        with patch("taskfile_help.taskfile_help.install_completion") as mock_install:
            mock_install.return_value = (False, "Installation failed")
            
            result = main(["script.py", "namespace", "--install-completion"])
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Installation failed" in captured.out


class TestSearchCommand:
    """Tests for search command functionality."""

    def test_search_with_single_pattern(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test search command with single pattern."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
  test:
    desc: Run tests
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "search", "build"])
        
        assert result == 0

    def test_search_with_multiple_patterns(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test search command with multiple patterns."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build-project:
    desc: Build the project
    cmds: []
  test:
    desc: Run tests
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "search", "build", "project"])
        
        assert result == 0

    def test_search_with_regex(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test search command with regex pattern."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
  rebuild:
    desc: Rebuild the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "search", "--regex", "^build"])
        
        assert result == 0

    def test_search_no_filters_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
        """Test search command without filters returns error."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "search"])
        
        assert result == 1


class TestNamespaceQuestionMark:
    """Tests for the '?' namespace feature."""

    def test_namespace_question_mark_with_namespaces(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
        """Test '?' namespace shows available namespaces."""
        # Create main taskfile
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        
        # Create namespace taskfiles
        dev_taskfile = tmp_path / "Taskfile-dev.yml"
        dev_taskfile.write_text("""version: '3'

tasks:
  test:
    desc: Run tests
    cmds: []
""")
        
        test_taskfile = tmp_path / "Taskfile-test.yml"
        test_taskfile.write_text("""version: '3'

tasks:
  lint:
    desc: Run linter
    cmds: []
""")
        
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "?"])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Available namespaces" in captured.out
        assert "dev" in captured.out
        assert "test" in captured.out

    def test_namespace_question_mark_no_namespaces(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test '?' namespace with no namespace taskfiles."""
        # Create only main taskfile
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "namespace", "?"])
        
        assert result == 0


class TestCollectAllTaskfiles:
    """Tests for _collect_all_taskfiles function (lines 302-303)."""

    def test_search_with_namespace_taskfiles(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test search collects tasks from namespace taskfiles."""
        # Create main taskfile
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        
        # Create namespace taskfile
        dev_taskfile = tmp_path / "Taskfile-dev.yml"
        dev_taskfile.write_text("""version: '3'

tasks:
  test:
    desc: Run tests
    cmds: []
  lint:
    desc: Run linter
    cmds: []
""")
        
        monkeypatch.chdir(tmp_path)
        
        with patch("sys.stdout.isatty", return_value=False):
            result = main(["script.py", "search", "test"])
        
        assert result == 0


class TestInvalidCommand:
    """Tests for invalid command error handling (lines 367-368)."""

    def test_invalid_command_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test invalid command returns error."""
        # Create a minimal taskfile
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds: []
""")
        
        monkeypatch.chdir(tmp_path)
        
        # Directly test by mocking the args to have an invalid command
        with patch("taskfile_help.config.Args.parse_args") as mock_parse:
            from taskfile_help.config import Args
            
            # Create args with invalid command
            mock_parse.return_value = Args(
                command="invalid_command",
                namespace="",
                patterns=None,
                regexes=None,
                no_color=False,
                search_dirs=None,
                verbose=False,
                json_output=False,
                completion=None,
                complete=None,
                install_completion=None,
                group_pattern=None,
            )
            
            with patch("sys.stdout.isatty", return_value=False):
                result = main(["script.py", "invalid_command"])
            
            assert result == 1
