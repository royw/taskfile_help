"""Unit tests for the search module."""

from taskfile_help.search import (
    filter_by_group,
    filter_by_namespace,
    filter_by_task,
    matches_pattern,
    matches_regex,
    search_taskfiles,
)


class TestMatchingFunctions:
    """Tests for pattern and regex matching functions."""

    def test_matches_pattern_case_insensitive(self) -> None:
        """Test case-insensitive pattern matching."""
        assert matches_pattern("BuildAll", "build")
        assert matches_pattern("test-unit", "TEST")
        assert matches_pattern("format", "FORMAT")

    def test_matches_pattern_substring(self) -> None:
        """Test substring matching."""
        assert matches_pattern("test-unit", "unit")
        assert matches_pattern("build-all", "all")
        assert matches_pattern("format-check", "check")

    def test_matches_pattern_no_match(self) -> None:
        """Test pattern not matching."""
        assert not matches_pattern("build", "test")
        assert not matches_pattern("format", "lint")

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


class TestFilterFunctions:
    """Tests for filter functions."""

    def test_filter_by_namespace_pattern(self) -> None:
        """Test filtering by namespace with pattern."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
            ("dev", [("Development", "serve", "Start server")]),
        ]
        
        results = filter_by_namespace(taskfiles, pattern="test")
        
        assert len(results) == 1
        assert results[0][0] == "test"
        assert results[0][4] == "namespace"

    def test_filter_by_namespace_regex(self) -> None:
        """Test filtering by namespace with regex."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
            ("dev", [("Development", "serve", "Start server")]),
        ]
        
        results = filter_by_namespace(taskfiles, pattern="dev", regex="^dev")
        
        assert len(results) == 1
        assert results[0][0] == "dev"

    def test_filter_by_namespace_no_match(self) -> None:
        """Test namespace filter with no matches."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        results = filter_by_namespace(taskfiles, pattern="nonexistent")
        
        assert len(results) == 0

    def test_filter_by_group_pattern(self) -> None:
        """Test filtering by group with pattern."""
        taskfiles = [
            ("test", [
                ("Testing", "unit", "Run unit tests"),
                ("Linting", "lint", "Run linter"),
            ]),
        ]
        
        results = filter_by_group(taskfiles, pattern="lint")
        
        assert len(results) == 1
        assert results[0][1] == "Linting"
        assert results[0][4] == "group"

    def test_filter_by_group_regex(self) -> None:
        """Test filtering by group with regex."""
        taskfiles = [
            ("test", [
                ("Testing", "unit", "Run unit tests"),
                ("Building", "build", "Build project"),
            ]),
        ]
        
        results = filter_by_group(taskfiles, pattern="Test", regex="^Test")
        
        assert len(results) == 1
        assert results[0][1] == "Testing"

    def test_filter_by_task_pattern(self) -> None:
        """Test filtering by task name with pattern."""
        taskfiles = [
            ("test", [
                ("Testing", "unit", "Run unit tests"),
                ("Testing", "integration", "Run integration tests"),
            ]),
        ]
        
        results = filter_by_task(taskfiles, pattern="unit")
        
        assert len(results) == 1
        assert results[0][2] == "unit"
        assert results[0][4] == "task"

    def test_filter_by_task_regex(self) -> None:
        """Test filtering by task name with regex."""
        taskfiles = [
            ("test", [
                ("Testing", "test-unit", "Run unit tests"),
                ("Testing", "test-integration", "Run integration tests"),
            ]),
        ]
        
        results = filter_by_task(taskfiles, pattern="test", regex="^test-")
        
        assert len(results) == 2
        assert all(r[2].startswith("test-") for r in results)

    def test_filter_by_task_combined_filters(self) -> None:
        """Test filtering by task with both pattern and regex."""
        taskfiles = [
            ("test", [
                ("Testing", "test-unit", "Run unit tests"),
                ("Testing", "unit-test", "Run unit tests"),
            ]),
        ]
        
        results = filter_by_task(taskfiles, pattern="unit", regex="^test")
        
        # Only test-unit matches both filters
        assert len(results) == 1
        assert results[0][2] == "test-unit"


class TestSearchTaskfiles:
    """Tests for search_taskfiles function."""

    def test_search_with_pattern(self) -> None:
        """Test search with pattern is required."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        # Pattern is now required
        results = search_taskfiles(taskfiles, pattern="test")
        
        assert len(results) > 0

    def test_search_by_pattern(self) -> None:
        """Test search by pattern."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
            ("dev", [("Development", "serve", "Start server")]),
        ]
        
        results = search_taskfiles(taskfiles, pattern="test")
        
        # Should match namespace "test" and show all its tasks
        assert len(results) > 0
        assert any(r[0] == "test" for r in results)

    def test_search_with_regex(self) -> None:
        """Test search with pattern and regex."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
            ("dev", [("Development", "serve", "Start server")]),
        ]
        
        results = search_taskfiles(taskfiles, pattern="dev", regex="^dev")
        
        assert len(results) > 0
        assert any(r[0] == "dev" for r in results)

    def test_search_combined_filters(self) -> None:
        """Test search with both pattern and regex."""
        taskfiles = [
            ("test", [
                ("Testing", "test-unit", "Run unit tests"),
                ("Testing", "unit-test", "Run unit tests"),
            ]),
        ]
        
        results = search_taskfiles(taskfiles, pattern="unit", regex="^test")
        
        # Should find test-unit (matches both)
        assert len(results) > 0

    def test_search_deduplication(self) -> None:
        """Test that search results are deduplicated."""
        taskfiles = [
            ("test", [("Testing", "test", "Run tests")]),
        ]
        
        # Search with pattern that matches both namespace and task
        results = search_taskfiles(taskfiles, pattern="test")
        
        # Task should only appear once even though it matches multiple criteria
        task_names = [r[2] for r in results]
        assert task_names.count("test") == 1

    def test_search_multiple_namespaces(self) -> None:
        """Test search across multiple namespaces."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
            ("dev", [("Testing", "integration", "Run integration tests")]),
        ]
        
        results = search_taskfiles(taskfiles, pattern="test")
        
        # Should find results from test namespace
        assert any(r[0] == "test" for r in results)

    def test_search_empty_taskfiles(self) -> None:
        """Test search with empty taskfiles list."""
        results = search_taskfiles([], pattern="test")
        
        assert results == []

    def test_search_no_matches(self) -> None:
        """Test search with no matching results."""
        taskfiles = [
            ("test", [("Testing", "unit", "Run unit tests")]),
        ]
        
        results = search_taskfiles(taskfiles, pattern="nonexistent")
        
        assert results == []
