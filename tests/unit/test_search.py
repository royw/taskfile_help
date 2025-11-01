"""Unit tests for the search module."""

from taskfile_help.search import (
    matches_all_patterns,
    matches_all_regexes,
    matches_regex,
    search_taskfiles,
    task_matches_filters,
)


class TestMatchingFunctions:
    """Tests for pattern and regex matching functions."""

    def test_matches_all_patterns_single(self) -> None:
        """Test matching with a single pattern."""
        assert matches_all_patterns("version-bump", ["version"])
        assert matches_all_patterns("version-bump", ["bump"])

    def test_matches_all_patterns_multiple(self) -> None:
        """Test matching with multiple patterns (AND logic)."""
        assert matches_all_patterns("version-bump", ["version", "bump"])
        assert matches_all_patterns("test-unit-coverage", ["test", "unit", "coverage"])
        assert matches_all_patterns("BuildAll", ["build", "all"])

    def test_matches_all_patterns_case_insensitive(self) -> None:
        """Test case-insensitive matching with multiple patterns."""
        assert matches_all_patterns("VERSION-BUMP", ["version", "bump"])
        assert matches_all_patterns("test-unit", ["TEST", "UNIT"])

    def test_matches_all_patterns_no_match(self) -> None:
        """Test when not all patterns match."""
        assert not matches_all_patterns("version-bump", ["version", "release"])
        assert not matches_all_patterns("test-unit", ["test", "integration"])
        assert not matches_all_patterns("build", ["build", "deploy"])

    def test_matches_regex_basic(self) -> None:
        """Test basic regex matching."""
        assert matches_regex("test", "^test")
        assert matches_regex("build-all", "all$")
        assert matches_regex("format", ".*mat")

    def test_matches_regex_no_match(self) -> None:
        """Test regex not matching."""
        assert not matches_regex("test", "^build")
        assert not matches_regex("format", "lint$")

    def test_matches_regex_invalid(self) -> None:
        """Test invalid regex returns False."""
        assert not matches_regex("test", "[invalid(")
        assert not matches_regex("build", "(?P<")

    def test_matches_all_regexes(self) -> None:
        """Test matching multiple regexes."""
        assert matches_all_regexes("test-unit", ["test", "unit"])
        assert matches_all_regexes("version-bump", ["^version", "bump$"])

    def test_matches_all_regexes_no_match(self) -> None:
        """Test when not all regexes match."""
        assert not matches_all_regexes("test-unit", ["test", "integration"])


class TestTaskMatchesFilters:
    """Tests for task_matches_filters function."""

    def test_task_matches_single_pattern(self) -> None:
        """Test task matching with a single pattern."""
        assert task_matches_filters(
            "version", "Version", "bump", "Bump version",
            patterns=["version"]
        )
        assert task_matches_filters(
            "version", "Version", "bump", "Bump version",
            patterns=["bump"]
        )

    def test_task_matches_multiple_patterns(self) -> None:
        """Test task matching with multiple patterns (AND logic)."""
        assert task_matches_filters(
            "version", "Version Management", "bump:minor", "Bump the minor version",
            patterns=["version", "minor"]
        )
        assert task_matches_filters(
            "test", "Testing", "unit", "Run unit tests",
            patterns=["test", "unit"]
        )

    def test_task_matches_patterns_across_fields(self) -> None:
        """Test patterns matching across different fields."""
        # "version" in namespace, "bump" in task name
        assert task_matches_filters(
            "version", "Management", "bump", "Update version",
            patterns=["version", "bump"]
        )
        # "test" in namespace, "unit" in description
        assert task_matches_filters(
            "test", "Testing", "run", "Run unit tests",
            patterns=["test", "unit"]
        )

    def test_task_no_match_patterns(self) -> None:
        """Test task not matching when patterns don't all match."""
        assert not task_matches_filters(
            "version", "Version", "bump", "Bump version",
            patterns=["version", "release"]
        )

    def test_task_matches_single_regex(self) -> None:
        """Test task matching with a single regex."""
        assert task_matches_filters(
            "version", "Version", "bump", "Bump version",
            regexes=["^version"]
        )

    def test_task_matches_multiple_regexes(self) -> None:
        """Test task matching with multiple regexes."""
        assert task_matches_filters(
            "test", "Testing", "unit", "Run unit tests",
            regexes=["test", "unit"]
        )

    def test_task_matches_patterns_and_regexes(self) -> None:
        """Test task matching with both patterns and regexes."""
        assert task_matches_filters(
            "version", "Version Management", "bump:minor", "Bump the minor version",
            patterns=["version"],
            regexes=["minor"]
        )


class TestSearchTaskfiles:
    """Tests for search_taskfiles function."""

    def test_search_with_single_pattern(self) -> None:
        """Test search with a single pattern."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        results = search_taskfiles(taskfiles, patterns=["test"])
        
        assert len(results) > 0
        assert results[0][0] == "test"

    def test_search_with_multiple_patterns(self) -> None:
        """Test search with multiple patterns (AND logic)."""
        taskfiles = [
            ("version", [
                ("Version", "bump", "Bump version"),
                ("Version", "bump:minor", "Bump the minor version"),
                ("Version", "check", "Check version"),
            ]),
        ]
        
        results = search_taskfiles(taskfiles, patterns=["version", "minor"])
        
        # Only bump:minor has both "version" (namespace) and "minor" (description)
        assert len(results) == 1
        assert results[0][2] == "bump:minor"

    def test_search_with_patterns_across_fields(self) -> None:
        """Test search with patterns matching across different fields."""
        taskfiles = [
            ("version", [
                ("Management", "bump", "Bump the version"),
            ]),
        ]
        
        results = search_taskfiles(taskfiles, patterns=["version", "bump"])
        
        # "version" in namespace, "bump" in task name and description
        assert len(results) == 1
        assert results[0][2] == "bump"

    def test_search_with_single_regex(self) -> None:
        """Test search with a single regex."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
            ("dev", [("Development", "serve", "Start server")]),
        ]
        
        results = search_taskfiles(taskfiles, regexes=["^test"])
        
        assert len(results) > 0
        assert results[0][0] == "test"

    def test_search_with_multiple_regexes(self) -> None:
        """Test search with multiple regexes."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        results = search_taskfiles(taskfiles, regexes=["test", "unit"])
        
        assert len(results) == 1
        assert results[0][2] == "unit"

    def test_search_with_patterns_and_regexes(self) -> None:
        """Test search with both patterns and regexes."""
        taskfiles = [
            ("version", [
                ("Version", "bump", "Bump version"),
                ("Version", "bump:minor", "Bump the minor version"),
            ]),
        ]
        
        results = search_taskfiles(taskfiles, patterns=["version"], regexes=["minor"])
        
        assert len(results) == 1
        assert results[0][2] == "bump:minor"

    def test_search_no_matches(self) -> None:
        """Test search with no matching results."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        results = search_taskfiles(taskfiles, patterns=["nonexistent"])
        
        assert results == []

    def test_search_empty_taskfiles(self) -> None:
        """Test search with empty taskfiles list."""
        results = search_taskfiles([], patterns=["test"])
        
        assert results == []

    def test_search_no_filters(self) -> None:
        """Test search with no filters returns empty."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        results = search_taskfiles(taskfiles)
        
        assert results == []
