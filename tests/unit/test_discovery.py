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

    def test_find_namespace_taskfile_not_found(self, tmp_path: Path) -> None:
        """Test when namespace taskfile is not found."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.find_namespace_taskfile("nonexistent")
        
        assert result is None

    def test_get_all_namespace_taskfiles_empty(self, tmp_path: Path) -> None:
        """Test getting namespace taskfiles when none exist."""
        discovery = TaskfileDiscovery([tmp_path])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0

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

    def test_handles_nonexistent_search_dir(self, tmp_path: Path) -> None:
        """Test nonexistent search directories are handled gracefully."""
        nonexistent = tmp_path / "nonexistent"
        
        discovery = TaskfileDiscovery([nonexistent])
        result = discovery.get_all_namespace_taskfiles()
        
        assert len(result) == 0



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
