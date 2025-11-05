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
        """Test .yml extension is preferred over .yaml."""
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

    def test_find_main_taskfile_lowercase_yml(self, tmp_path: Path) -> None:
        """Test finding lowercase taskfile.yml."""
        taskfile = tmp_path / "taskfile.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result == taskfile

    def test_find_main_taskfile_lowercase_yaml(self, tmp_path: Path) -> None:
        """Test finding lowercase taskfile.yaml."""
        taskfile = tmp_path / "taskfile.yaml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result == taskfile

    def test_find_main_taskfile_prefers_uppercase(self, tmp_path: Path) -> None:
        """Test uppercase Taskfile is preferred over lowercase."""
        uppercase = tmp_path / "Taskfile.yml"
        lowercase = tmp_path / "taskfile.yml"
        uppercase.write_text("version: '3'\ntasks: {}")
        lowercase.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_main_taskfile()
        
        assert result == uppercase

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
        """Test namespace taskfiles are sorted alphabetically."""
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
        """Test main taskfile is excluded from namespace list."""
        (tmp_path / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_get_all_namespace_taskfiles_removes_duplicates(self, tmp_path: Path) -> None:
        """Test duplicate namespaces are removed."""
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
        
        assert len(result) == 8
        assert tmp_path / "Taskfile.yml" in result
        assert tmp_path / "Taskfile.yaml" in result
        assert tmp_path / "taskfile.yml" in result
        assert tmp_path / "taskfile.yaml" in result
        assert tmp_path / "Taskfile.dist.yml" in result
        assert tmp_path / "Taskfile.dist.yaml" in result
        assert tmp_path / "taskfile.dist.yml" in result
        assert tmp_path / "taskfile.dist.yaml" in result

    def test_get_possible_paths_empty_namespace(self, tmp_path: Path) -> None:
        """Test getting possible paths for empty namespace."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_possible_paths("")
        
        assert len(result) == 8
        assert tmp_path / "Taskfile.yml" in result
        assert tmp_path / "Taskfile.yaml" in result
        assert tmp_path / "taskfile.yml" in result
        assert tmp_path / "taskfile.yaml" in result
        assert tmp_path / "Taskfile.dist.yml" in result
        assert tmp_path / "Taskfile.dist.yaml" in result
        assert tmp_path / "taskfile.dist.yml" in result
        assert tmp_path / "taskfile.dist.yaml" in result

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
        """Test search directory order determines precedence (first match wins)."""
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

    def test_namespace_with_underscores(self, tmp_path: Path) -> None:
        """Test namespace with underscores in the name."""
        taskfile = tmp_path / "Taskfile-my_namespace.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 1
        assert result[0][0] == "my_namespace"
        assert result[0][1] == taskfile

    def test_namespace_with_numbers(self, tmp_path: Path) -> None:
        """Test namespace with numbers in the name."""
        taskfile = tmp_path / "Taskfile-v2_prod.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 1
        assert result[0][0] == "v2_prod"

    def test_lowercase_taskfile_prefix(self, tmp_path: Path) -> None:
        """Test lowercase 'taskfile' prefix is recognized."""
        taskfile = tmp_path / "taskfile-dev.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_mixed_case_taskfile_prefix(self, tmp_path: Path) -> None:
        """Test mixed case 'Taskfile' prefix is recognized."""
        taskfile = tmp_path / "Taskfile-dev.yml"
        taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_ignores_wrong_extension(self, tmp_path: Path) -> None:
        """Test files with wrong extensions are ignored."""
        (tmp_path / "Taskfile-dev.txt").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-dev.json").write_text("{}")
        (tmp_path / "Taskfile-dev.py").write_text("# python file")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0

    def test_ignores_wrong_prefix(self, tmp_path: Path) -> None:
        """Test files with wrong prefix are ignored."""
        (tmp_path / "MyTaskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Task-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "taskfile-dev.yml").write_text("version: '3'\ntasks: {}")  # Valid one
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Only the valid lowercase taskfile should be found
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_ignores_empty_namespace(self, tmp_path: Path) -> None:
        """Test files with empty namespace are ignored."""
        (tmp_path / "Taskfile-.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile_.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0

    def test_ignores_directories(self, tmp_path: Path) -> None:
        """Test directories matching the pattern are ignored."""
        # Create a directory that matches the pattern
        dir_with_pattern = tmp_path / "Taskfile-dev.yml"
        dir_with_pattern.mkdir()
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0

    def test_handles_nonexistent_search_dir(self, tmp_path: Path) -> None:
        """Test nonexistent search directories are handled gracefully."""
        nonexistent = tmp_path / "nonexistent"
        
        discovery = TaskfileDiscovery([nonexistent])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0

    def test_multiple_namespaces_mixed_separators(self, tmp_path: Path) -> None:
        """Test multiple namespaces with mixed separators and extensions."""
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile_prod.yaml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "taskfile-test.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "taskfile_staging.yaml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 4
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"dev", "prod", "test", "staging"}


class TestTaskfileDiscoveryIncludes:
    """Tests for includes-based namespace discovery."""

    def test_parse_includes_basic(self, tmp_path: Path) -> None:
        """Test parsing basic includes section from main Taskfile."""
        # Create main Taskfile with includes
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
    dir: .
  prod:
    taskfile: ./Taskfile-prod.yml
    dir: .
tasks: {}
""")
        
        # Create included taskfiles
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-prod.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"dev", "prod"}

    def test_parse_includes_with_subdirectory(self, tmp_path: Path) -> None:
        """Test parsing includes with taskfiles in subdirectory."""
        # Create main Taskfile with includes pointing to subdirectory
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  git:
    taskfile: ./taskfiles/Taskfile-git.yml
    dir: .
  version:
    taskfile: ./taskfiles/Taskfile-version.yml
    dir: .
tasks: {}
""")
        
        # Create subdirectory and included taskfiles
        taskfiles_dir = tmp_path / "taskfiles"
        taskfiles_dir.mkdir()
        (taskfiles_dir / "Taskfile-git.yml").write_text("version: '3'\ntasks: {}")
        (taskfiles_dir / "Taskfile-version.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"git", "version"}
        
        # Verify paths are correct
        for ns, path in result:
            assert path.exists()
            assert path.parent == taskfiles_dir

    def test_parse_includes_simple_string_format(self, tmp_path: Path) -> None:
        """Test parsing includes with simple string format."""
        # Create main Taskfile with simple string includes
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  dev: ./Taskfile-dev.yml
  prod: ./Taskfile-prod.yml
tasks: {}
""")
        
        # Create included taskfiles
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-prod.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"dev", "prod"}

    def test_parse_includes_ignores_nonexistent_files(self, tmp_path: Path) -> None:
        """Test includes parsing ignores references to nonexistent files."""
        # Create main Taskfile with includes (one file exists, one doesn't)
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
    dir: .
  prod:
    taskfile: ./Taskfile-prod.yml
    dir: .
tasks: {}
""")
        
        # Only create dev taskfile
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should only find dev, not prod
        assert len(result) == 1
        assert result[0][0] == "dev"

    def test_parse_includes_fallback_to_filename_when_no_includes(self, tmp_path: Path) -> None:
        """Test falls back to filename-based discovery when no includes section."""
        # Create main Taskfile without includes
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("version: '3'\ntasks: {}")
        
        # Create namespace taskfiles using filename pattern
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-prod.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find both via filename pattern
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"dev", "prod"}

    def test_parse_includes_fallback_when_no_main_taskfile(self, tmp_path: Path) -> None:
        """Test falls back to filename-based discovery when no main Taskfile exists."""
        # Create namespace taskfiles using filename pattern (no main Taskfile)
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-prod.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find both via filename pattern
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"dev", "prod"}

    def test_find_namespace_taskfile_from_includes(self, tmp_path: Path) -> None:
        """Test finding a specific namespace taskfile from includes."""
        # Create main Taskfile with includes
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  git:
    taskfile: ./taskfiles/Taskfile-git.yml
    dir: .
tasks: {}
""")
        
        # Create included taskfile
        taskfiles_dir = tmp_path / "taskfiles"
        taskfiles_dir.mkdir()
        git_taskfile = taskfiles_dir / "Taskfile-git.yml"
        git_taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("git")
        
        assert result == git_taskfile

    def test_includes_takes_precedence_over_filename(self, tmp_path: Path) -> None:
        """Test includes section takes precedence over filename-based discovery."""
        # Create main Taskfile with includes pointing to subdirectory
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./taskfiles/Taskfile-dev.yml
    dir: .
tasks: {}
""")
        
        # Create taskfile in subdirectory (should be found)
        taskfiles_dir = tmp_path / "taskfiles"
        taskfiles_dir.mkdir()
        correct_taskfile = taskfiles_dir / "Taskfile-dev.yml"
        correct_taskfile.write_text("version: '3'\ntasks: {}")
        
        # Create taskfile in main directory (should be ignored)
        wrong_taskfile = tmp_path / "Taskfile-dev.yml"
        wrong_taskfile.write_text("version: '3'\ntasks: {wrong: content}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("dev")
        
        # Should find the one from includes, not the filename-based one
        assert result == correct_taskfile

    def test_parse_includes_with_mixed_formats(self, tmp_path: Path) -> None:
        """Test parsing includes with mixed dict and string formats."""
        # Create main Taskfile with mixed includes formats
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
    dir: .
  prod: ./Taskfile-prod.yml
tasks: {}
""")
        
        # Create included taskfiles
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        (tmp_path / "Taskfile-prod.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"dev", "prod"}

    def test_parse_includes_caching(self, tmp_path: Path) -> None:
        """Test includes are cached and not re-parsed on subsequent calls."""
        # Create main Taskfile with includes
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  dev:
    taskfile: ./Taskfile-dev.yml
    dir: .
tasks: {}
""")
        
        # Create included taskfile
        (tmp_path / "Taskfile-dev.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        
        # First call should parse and cache
        result1 = discovery.get_all_namespace_taskfiles()
        
        # Second call should use cache
        result2 = discovery.get_all_namespace_taskfiles()
        
        # Results should be identical
        assert result1 == result2
        assert len(result1) == 1
        assert result1[0][0] == "dev"
