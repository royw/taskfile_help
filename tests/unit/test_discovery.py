"""Unit tests for the discovery module."""

from pathlib import Path

import pytest

from taskfile_help.discovery import TaskfileDiscovery


class TestTaskfileDiscovery:
    """Tests for TaskfileDiscovery class."""

    def test_find_main_taskfile_yml(self, tmp_path: Path) -> None:
        """Test finding main Taskfile.yml."""
        taskfile = tmp_path / "Taskfile.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result == taskfile

    def test_find_main_taskfile_yaml(self, tmp_path: Path) -> None:
        """Test finding main Taskfile.yaml."""
        taskfile = tmp_path / "Taskfile.yaml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result == taskfile

    def test_find_main_taskfile_prefers_yml(self, tmp_path: Path) -> None:
        """Test that .yml is preferred over .yaml."""
        yml_file = tmp_path / "Taskfile.yml"
        yaml_file = tmp_path / "Taskfile.yaml"
        yml_file.write_text("version: '3'\ntasks: {}")
        yaml_file.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result == yml_file

    def test_find_main_taskfile_not_found(self, tmp_path: Path) -> None:
        """Test when main taskfile is not found."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result is None

    def test_find_main_taskfile_multiple_dirs(self, tmp_path: Path) -> None:
        """Test finding main taskfile in multiple directories."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        taskfile = dir2 / "Taskfile.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([dir1, dir2])
        result = discovery.find_main_taskfile()
        
        assert result == taskfile

    def test_find_namespace_taskfile_hyphen(self, tmp_path: Path) -> None:
        """Test finding namespace taskfile with hyphen separator."""
        taskfile = tmp_path / "Taskfile-dev.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("dev")
        
        assert result == taskfile

    def test_find_namespace_taskfile_underscore(self, tmp_path: Path) -> None:
        """Test finding namespace taskfile with underscore separator."""
        taskfile = tmp_path / "Taskfile_dev.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("dev")
        
        assert result == taskfile

    def test_find_namespace_taskfile_yaml_extension(self, tmp_path: Path) -> None:
        """Test finding namespace taskfile with .yaml extension."""
        taskfile = tmp_path / "Taskfile-dev.yaml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("dev")
        
        assert result == taskfile

    def test_find_namespace_taskfile_not_found(self, tmp_path: Path) -> None:
        """Test when namespace taskfile is not found."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("nonexistent")
        
        assert result is None

    def test_get_all_namespace_taskfiles(self, tmp_path: Path) -> None:
        """Test getting all namespace taskfiles."""
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-prod.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-test.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 3
        namespaces = [ns for ns, _ in result]
        assert "dev" in namespaces
        assert "prod" in namespaces
        assert "test" in namespaces

    def test_get_all_namespace_taskfiles_sorted(self, tmp_path: Path) -> None:
        """Test that namespace taskfiles are sorted."""
        (tmp_path / "Taskfile-zebra.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-alpha.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-beta.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        namespaces = [ns for ns, _ in result]
        assert namespaces == ["alpha", "beta", "zebra"]

    def test_get_all_namespace_taskfiles_empty(self, tmp_path: Path) -> None:
        """Test getting namespace taskfiles when none exist."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0

    def test_get_all_namespace_taskfiles_ignores_main(self, tmp_path: Path) -> None:
        """Test that main taskfile is not included in namespace list."""
        (tmp_path / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_get_all_namespace_taskfiles_removes_duplicates(self, tmp_path: Path) -> None:
        """Test that duplicate namespaces are removed."""
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile_dev.yaml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should only have one 'dev' namespace
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_get_possible_paths_main(self, tmp_path: Path) -> None:
        """Test getting possible paths for main taskfile."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_possible_paths("main")
        
        assert len(result) == 2
        assert tmp_path / "Taskfile.yml" in result
        assert tmp_path / "Taskfile.yaml" in result

    def test_get_possible_paths_empty_namespace(self, tmp_path: Path) -> None:
        """Test getting possible paths for empty namespace."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_possible_paths("")
        
        assert len(result) == 2
        assert tmp_path / "Taskfile.yml" in result
        assert tmp_path / "Taskfile.yaml" in result

    def test_get_possible_paths_namespace(self, tmp_path: Path) -> None:
        """Test getting possible paths for a namespace."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_possible_paths("dev")
        
        assert len(result) == 4
        assert tmp_path / "Taskfile-dev.yml" in result
        assert tmp_path / "Taskfile-dev.yaml" in result
        assert tmp_path / "Taskfile_dev.yml" in result
        assert tmp_path / "Taskfile_dev.yaml" in result

    def test_get_possible_paths_multiple_dirs(self, tmp_path: Path) -> None:
        """Test getting possible paths across multiple directories."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        discovery = TaskfileDiscovery([dir1, dir2])
        result = discovery.get_possible_paths("dev")
        
        assert len(result) == 8  # 4 patterns × 2 directories
        assert dir1 / "Taskfile-dev.yml" in result
        assert dir2 / "Taskfile-dev.yml" in result

    def test_search_dirs_order_matters(self, tmp_path: Path) -> None:
        """Test that search directory order matters (first match wins)."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        taskfile1 = dir1 / "Taskfile-dev.yml"
        taskfile2 = dir2 / "Taskfile-dev.yml"
        taskfile1.write_text("version: '3'\ntasks: {}")
        taskfile2.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([dir1, dir2])
        result = discovery.find_namespace_taskfile("dev")
        
        assert result == taskfile1
