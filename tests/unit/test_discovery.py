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


class TestTaskfileDiscoveryNestedIncludes:
    """Tests for nested/recursive includes support."""

    def test_nested_includes_basic(self, tmp_path: Path) -> None:
        """Test basic nested includes with two levels."""
        # Create main Taskfile
        main_taskfile = tmp_path / "Taskfile.yml"
        main_taskfile.write_text("""version: '3'
includes:
  foo:
    taskfile: ./foo/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create foo directory and taskfile with nested include
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar:
    taskfile: ../bar/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create bar directory and taskfile
        bar_dir = tmp_path / "bar"
        bar_dir.mkdir()
        (bar_dir / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find both foo and foo:bar
        assert len(result) == 2
        namespaces = [ns for ns, _ in result]
        assert "foo" in namespaces
        assert "foo:bar" in namespaces
        
        # Verify paths
        namespace_dict = dict(result)
        assert namespace_dict["foo"] == foo_dir / "Taskfile.yml"
        assert namespace_dict["foo:bar"] == bar_dir / "Taskfile.yml"

    def test_nested_includes_three_levels(self, tmp_path: Path) -> None:
        """Test nested includes with three levels (foo:bar:baz)."""
        # Create main Taskfile
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  foo:
    taskfile: ./foo/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create foo
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar:
    taskfile: ./bar/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create bar
        bar_dir = foo_dir / "bar"
        bar_dir.mkdir()
        (bar_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  baz:
    taskfile: ./baz/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create baz
        baz_dir = bar_dir / "baz"
        baz_dir.mkdir()
        (baz_dir / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find foo, foo:bar, and foo:bar:baz
        assert len(result) == 3
        namespaces = [ns for ns, _ in result]
        assert "foo" in namespaces
        assert "foo:bar" in namespaces
        assert "foo:bar:baz" in namespaces

    def test_nested_includes_multiple_branches(self, tmp_path: Path) -> None:
        """Test nested includes with multiple branches."""
        # Create main Taskfile with two top-level includes
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  foo:
    taskfile: ./foo/Taskfile.yml
    dir: .
  qux:
    taskfile: ./qux/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create foo with nested include
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar:
    taskfile: ./bar/Taskfile.yml
    dir: .
tasks: {}
""")
        
        bar_dir = foo_dir / "bar"
        bar_dir.mkdir()
        (bar_dir / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        
        # Create qux with nested include
        qux_dir = tmp_path / "qux"
        qux_dir.mkdir()
        (qux_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  quux:
    taskfile: ./quux/Taskfile.yml
    dir: .
tasks: {}
""")
        
        quux_dir = qux_dir / "quux"
        quux_dir.mkdir()
        (quux_dir / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find all namespaces
        assert len(result) == 4
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"foo", "foo:bar", "qux", "qux:quux"}

    def test_nested_includes_circular_reference_prevention(self, tmp_path: Path) -> None:
        """Test circular reference prevention in nested includes."""
        # Create main Taskfile
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  foo:
    taskfile: ./foo/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create foo that includes bar
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar:
    taskfile: ../bar/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create bar that includes foo (circular reference)
        bar_dir = tmp_path / "bar"
        bar_dir.mkdir()
        (bar_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  foo:
    taskfile: ../foo/Taskfile.yml
    dir: .
tasks: {}
""")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should handle circular reference gracefully
        # Should find foo and foo:bar, but not infinite recursion
        namespaces = [ns for ns, _ in result]
        assert "foo" in namespaces
        assert "foo:bar" in namespaces
        # Should not have foo:bar:foo (circular)
        assert len(result) == 2

    def test_find_namespace_taskfile_nested(self, tmp_path: Path) -> None:
        """Test finding a specific nested namespace taskfile."""
        # Create nested structure
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  foo:
    taskfile: ./foo/Taskfile.yml
    dir: .
tasks: {}
""")
        
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar:
    taskfile: ./bar/Taskfile.yml
    dir: .
tasks: {}
""")
        
        bar_dir = foo_dir / "bar"
        bar_dir.mkdir()
        bar_taskfile = bar_dir / "Taskfile.yml"
        bar_taskfile.write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        
        # Should find the nested namespace
        result = discovery.find_namespace_taskfile("foo:bar")
        assert result == bar_taskfile

    def test_nested_includes_with_simple_string_format(self, tmp_path: Path) -> None:
        """Test nested includes using simple string format."""
        # Create main Taskfile with simple string format
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  foo: ./foo/Taskfile.yml
tasks: {}
""")
        
        # Create foo with simple string format
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar: ./bar/Taskfile.yml
tasks: {}
""")
        
        bar_dir = foo_dir / "bar"
        bar_dir.mkdir()
        (bar_dir / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find both namespaces
        namespaces = [ns for ns, _ in result]
        assert "foo" in namespaces
        assert "foo:bar" in namespaces

    def test_nested_includes_ignores_nonexistent_files(self, tmp_path: Path) -> None:
        """Test nested includes gracefully handles nonexistent files."""
        # Create main Taskfile
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  foo:
    taskfile: ./foo/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create foo with include to nonexistent file
        foo_dir = tmp_path / "foo"
        foo_dir.mkdir()
        (foo_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  bar:
    taskfile: ./nonexistent/Taskfile.yml
    dir: .
tasks: {}
""")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find foo but not foo:bar
        assert len(result) == 1
        assert result[0][0] == "foo"

    def test_nested_includes_mixed_with_flat(self, tmp_path: Path) -> None:
        """Test mixing nested and flat includes."""
        # Create main Taskfile with both flat and nested includes
        (tmp_path / "Taskfile.yml").write_text("""version: '3'
includes:
  flat:
    taskfile: ./Taskfile-flat.yml
    dir: .
  nested:
    taskfile: ./nested/Taskfile.yml
    dir: .
tasks: {}
""")
        
        # Create flat taskfile (no nested includes)
        (tmp_path / "Taskfile-flat.yml").write_text("version: '3'\ntasks: {}")
        
        # Create nested taskfile with includes
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        (nested_dir / "Taskfile.yml").write_text("""version: '3'
includes:
  deep:
    taskfile: ./deep/Taskfile.yml
    dir: .
tasks: {}
""")
        
        deep_dir = nested_dir / "deep"
        deep_dir.mkdir()
        (deep_dir / "Taskfile.yml").write_text("version: '3'\ntasks: {}")
        
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        # Should find all namespaces
        namespaces = [ns for ns, _ in result]
        assert set(namespaces) == {"flat", "nested", "nested:deep"}
