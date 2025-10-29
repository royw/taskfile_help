"""Unit tests for completion module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from taskfile_help.completion import (
    _complete_flags,
    _complete_namespace,
    _complete_task_name,
    generate_bash_completion,
    generate_fish_completion,
    generate_ksh_completion,
    generate_tcsh_completion,
    generate_zsh_completion,
    get_completions,
    install_completion,
)


class TestGetCompletions:
    """Tests for get_completions function."""

    def test_complete_namespace_without_colon(self, tmp_path: Path) -> None:
        """Test completing namespace names."""
        # Create test taskfiles
        (tmp_path / "Taskfile.yml").write_text("version: '3'\ntasks:\n  test:\n    desc: Test task\n")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks:\n  build:\n    desc: Build task\n")

        completions = get_completions("d", [tmp_path])
        assert "dev" in completions

    def test_complete_task_name_with_colon(self, tmp_path: Path) -> None:
        """Test completing task names within a namespace."""
        # Create test taskfile
        (tmp_path / "Taskfile-dev.yml").write_text(
            "version: '3'\ntasks:\n  build:\n    desc: Build task\n  deploy:\n    desc: Deploy task\n"
        )

        completions = get_completions("dev:d", [tmp_path])
        assert "dev:deploy" in completions

    def test_complete_flags(self, tmp_path: Path) -> None:
        """Test completing command-line flags."""
        completions = get_completions("--no", [tmp_path])
        assert "--no-color" in completions

    def test_empty_word_returns_all_namespaces(self, tmp_path: Path) -> None:
        """Test that empty word returns all available namespaces."""
        (tmp_path / "Taskfile.yml").write_text("version: '3'\ntasks:\n  test:\n    desc: Test\n")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks:\n  build:\n    desc: Build\n")

        completions = get_completions("", [tmp_path])
        assert "main" in completions
        assert "all" in completions
        assert "dev" in completions


class TestCompleteNamespace:
    """Tests for _complete_namespace function."""

    def test_returns_main_and_all(self, tmp_path: Path) -> None:
        """Test that main and all are always included."""
        completions = _complete_namespace("", [tmp_path])
        assert "main" in completions
        assert "all" in completions

    def test_filters_by_partial_match(self, tmp_path: Path) -> None:
        """Test filtering namespaces by partial match."""
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\n")
        (tmp_path / "Taskfile-deploy.yml").write_text("version: '3'\n")
        (tmp_path / "Taskfile-test.yml").write_text("version: '3'\n")

        completions = _complete_namespace("de", [tmp_path])
        assert "dev" in completions
        assert "deploy" in completions
        assert "test" not in completions

    def test_discovers_namespace_taskfiles(self, tmp_path: Path) -> None:
        """Test that namespace taskfiles are discovered."""
        (tmp_path / "Taskfile-custom.yml").write_text("version: '3'\n")

        completions = _complete_namespace("", [tmp_path])
        assert "custom" in completions


class TestCompleteTaskName:
    """Tests for _complete_task_name function."""

    def test_completes_tasks_in_namespace(self, tmp_path: Path) -> None:
        """Test completing task names within a namespace."""
        (tmp_path / "Taskfile-dev.yml").write_text(
            "version: '3'\ntasks:\n  build:\n    desc: Build\n  test:\n    desc: Test\n"
        )

        completions = _complete_task_name("dev", "b", [tmp_path])
        assert "dev:build" in completions
        assert "dev:test" not in completions

    def test_completes_tasks_in_main_namespace(self, tmp_path: Path) -> None:
        """Test completing task names in main namespace."""
        (tmp_path / "Taskfile.yml").write_text(
            "version: '3'\ntasks:\n  start:\n    desc: Start\n  stop:\n    desc: Stop\n"
        )

        completions = _complete_task_name("main", "st", [tmp_path])
        assert "start" in completions or "stop" in completions

    def test_returns_empty_for_nonexistent_namespace(self, tmp_path: Path) -> None:
        """Test that empty list is returned for nonexistent namespace."""
        completions = _complete_task_name("nonexistent", "task", [tmp_path])
        assert completions == []

    def test_handles_parsing_errors_gracefully(self, tmp_path: Path) -> None:
        """Test that parsing errors are handled gracefully."""
        (tmp_path / "Taskfile-broken.yml").write_text("invalid: yaml: content:")

        completions = _complete_task_name("broken", "task", [tmp_path])
        assert completions == []

    def test_handles_parse_taskfile_exception(self, tmp_path: Path) -> None:
        """Test that exceptions from parse_taskfile are caught and handled."""
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks:\n  build:\n    desc: Build\n")

        # Mock parse_taskfile to raise an exception
        with patch("taskfile_help.completion.parse_taskfile") as mock_parse:
            mock_parse.side_effect = RuntimeError("Unexpected error during parsing")
            
            completions = _complete_task_name("dev", "build", [tmp_path])
            
            # Should return empty list instead of crashing
            assert completions == []
            # Verify parse_taskfile was called
            assert mock_parse.called


class TestCompleteFlags:
    """Tests for _complete_flags function."""

    def test_completes_long_flags(self) -> None:
        """Test completing long flags."""
        completions = _complete_flags("--no")
        assert "--no-color" in completions

    def test_completes_short_flags(self) -> None:
        """Test completing short flags."""
        completions = _complete_flags("-v")
        assert "-v" in completions

    def test_returns_all_flags_for_dash(self) -> None:
        """Test that all flags starting with - are returned."""
        completions = _complete_flags("-")
        assert len(completions) > 0
        assert all(flag.startswith("-") for flag in completions)

    def test_returns_empty_for_non_flag(self) -> None:
        """Test that empty list is returned for non-flag input."""
        completions = _complete_flags("namespace")
        assert completions == []


class TestGenerateCompletionScripts:
    """Tests for completion script generation functions."""

    def test_generate_bash_completion(self) -> None:
        """Test bash completion script generation."""
        script = generate_bash_completion()
        assert "complete -F _taskfile_help_completion taskfile-help" in script
        assert "_taskfile_help_completion()" in script
        assert "taskfile-help --complete" in script

    def test_generate_zsh_completion(self) -> None:
        """Test zsh completion script generation."""
        script = generate_zsh_completion()
        assert "#compdef taskfile-help" in script
        assert "_taskfile_help()" in script
        assert "taskfile-help --complete" in script

    def test_generate_fish_completion(self) -> None:
        """Test fish completion script generation."""
        script = generate_fish_completion()
        assert "complete -c taskfile-help" in script
        assert "taskfile-help --complete" in script

    def test_generate_tcsh_completion(self) -> None:
        """Test tcsh completion script generation."""
        script = generate_tcsh_completion()
        assert "complete taskfile-help" in script
        assert "taskfile-help --complete" in script

    def test_generate_ksh_completion(self) -> None:
        """Test ksh completion script generation."""
        script = generate_ksh_completion()
        assert "_taskfile_help_complete" in script
        assert "taskfile-help --complete" in script


class TestInstallCompletion:
    """Tests for install_completion function."""

    @patch.dict("os.environ", {"SHELL": "/bin/bash"})
    def test_auto_detect_shell_from_environment(self, tmp_path: Path) -> None:
        """Test auto-detecting shell from $SHELL environment variable."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion(None)
            assert success
            assert "bash" in message.lower()

    @patch.dict("os.environ", {}, clear=True)
    def test_fails_when_shell_cannot_be_detected(self) -> None:
        """Test failure when shell cannot be auto-detected."""
        success, message = install_completion(None)
        assert not success
        assert "Could not detect shell" in message

    def test_fails_for_unsupported_shell(self) -> None:
        """Test failure for unsupported shell."""
        success, message = install_completion("powershell")
        assert not success
        assert "Unsupported shell" in message

    def test_installs_bash_completion(self, tmp_path: Path) -> None:
        """Test installing bash completion script."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("bash")
            assert success
            assert (tmp_path / ".bash_completion.d" / "taskfile-help").exists()
            assert "source" in message

    def test_installs_zsh_completion(self, tmp_path: Path) -> None:
        """Test installing zsh completion script."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("zsh")
            assert success
            assert (tmp_path / ".zsh" / "completion" / "_taskfile-help").exists()
            assert "fpath" in message

    def test_installs_fish_completion(self, tmp_path: Path) -> None:
        """Test installing fish completion script."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("fish")
            assert success
            assert (tmp_path / ".config" / "fish" / "completions" / "taskfile-help.fish").exists()

    def test_handles_csh_as_tcsh(self, tmp_path: Path) -> None:
        """Test that csh is handled as tcsh."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("csh")
            assert success
            assert (tmp_path / ".tcshrc.d" / "taskfile-help.tcsh").exists()

    def test_installs_tcsh_completion(self, tmp_path: Path) -> None:
        """Test installing tcsh completion script."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("tcsh")
            assert success
            assert (tmp_path / ".tcshrc.d" / "taskfile-help.tcsh").exists()
            assert "~/.tcshrc" in message

    def test_installs_ksh_completion(self, tmp_path: Path) -> None:
        """Test installing ksh completion script."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("ksh")
            assert success
            assert (tmp_path / ".kshrc.d" / "taskfile-help.ksh").exists()
            assert "~/.kshrc" in message

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that parent directories are created if they don't exist."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success, message = install_completion("bash")
            assert success
            assert (tmp_path / ".bash_completion.d").exists()

    def test_overwrites_existing_completion_script(self, tmp_path: Path) -> None:
        """Test that existing completion script is overwritten."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            # Install once
            install_completion("bash")
            original_content = (tmp_path / ".bash_completion.d" / "taskfile-help").read_text()

            # Install again
            success, message = install_completion("bash")
            assert success
            new_content = (tmp_path / ".bash_completion.d" / "taskfile-help").read_text()
            assert new_content == original_content  # Should be the same script

    def test_fails_when_path_is_readonly(self, tmp_path: Path) -> None:
        """Test that installation fails gracefully when path is read-only."""
        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        completion_dir = readonly_dir / ".bash_completion.d"
        completion_dir.mkdir()
        
        # Make the completion directory read-only
        completion_dir.chmod(0o444)
        
        try:
            with patch("pathlib.Path.home", return_value=readonly_dir):
                success, message = install_completion("bash")
                assert not success
                assert "Failed to write completion script" in message
        finally:
            # Restore permissions for cleanup
            completion_dir.chmod(0o755)

    def test_unsupported_shell_in_sourcing_instructions(self, tmp_path: Path) -> None:
        """Test that _get_sourcing_instructions handles unsupported shells gracefully."""
        from taskfile_help.completion import _get_sourcing_instructions
        
        # Test with an unsupported shell that somehow got past validation
        fake_path = tmp_path / "completion_script"
        instructions = _get_sourcing_instructions("unsupported_shell", fake_path)
        
        assert "Unsupported shell: unsupported_shell" in instructions


class TestIntegration:
    """Integration tests for completion functionality."""

    def test_complete_workflow_bash(self, tmp_path: Path) -> None:
        """Test complete workflow: discover, complete, generate."""
        # Setup test environment
        (tmp_path / "Taskfile.yml").write_text("version: '3'\ntasks:\n  build:\n    desc: Build\n")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks:\n  test:\n    desc: Test\n")

        # Test namespace completion
        namespaces = get_completions("", [tmp_path])
        assert "main" in namespaces
        assert "dev" in namespaces

        # Test task completion
        tasks = get_completions("dev:", [tmp_path])
        assert "dev:test" in tasks

        # Test script generation
        script = generate_bash_completion()
        assert "taskfile-help --complete" in script

    def test_partial_namespace_completion(self, tmp_path: Path) -> None:
        """Test partial namespace completion."""
        (tmp_path / "Taskfile-development.yml").write_text("version: '3'\n")
        (tmp_path / "Taskfile-deploy.yml").write_text("version: '3'\n")
        (tmp_path / "Taskfile-test.yml").write_text("version: '3'\n")

        completions = get_completions("de", [tmp_path])
        assert "development" in completions
        assert "deploy" in completions
        assert "test" not in completions

    def test_partial_task_completion(self, tmp_path: Path) -> None:
        """Test partial task name completion."""
        (tmp_path / "Taskfile-dev.yml").write_text(
            "version: '3'\ntasks:\n  build:\n    desc: Build\n  build-all:\n    desc: Build all\n  test:\n    desc: Test\n"
        )

        completions = get_completions("dev:build", [tmp_path])
        assert "dev:build" in completions
        assert "dev:build-all" in completions
        assert "dev:test" not in completions
