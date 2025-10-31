"""Search and filter functionality for taskfiles.

This module provides functions to search and filter tasks across namespaces,
groups, and task names using pattern matching or regular expressions.
"""

from __future__ import annotations

import re


# Type alias for task tuples: (group, task_name, description)
Task = tuple[str, str, str]
# Type alias for taskfile data: (namespace, tasks)
Taskfile = tuple[str, list[Task]]
# Type alias for search results with context
SearchResult = tuple[str, str, str, str, str]  # (namespace, group, task_name, description, match_type)


def matches_pattern(text: str, pattern: str) -> bool:
    """Check if text matches pattern using case-insensitive substring match.

    Args:
        text: Text to search in
        pattern: Pattern to search for

    Returns:
        True if pattern is found in text (case-insensitive), False otherwise
    """
    return pattern.lower() in text.lower()


def matches_regex(text: str, regex_pattern: str) -> bool:
    """Check if text matches regex pattern.

    Args:
        text: Text to search in
        regex_pattern: Regular expression pattern

    Returns:
        True if regex matches, False otherwise or if regex is invalid
    """
    try:
        return bool(re.search(regex_pattern, text))
    except re.error:
        return False


def matches_filters(text: str, pattern: str | None, regex: str | None) -> bool:
    """Check if text matches both pattern and regex filters.

    Args:
        text: Text to check against filters
        pattern: Optional pattern for substring matching
        regex: Optional regex pattern for matching

    Returns:
        True if text matches all provided filters, False otherwise
    """
    if pattern and not matches_pattern(text, pattern):
        return False
    return not (regex and not matches_regex(text, regex))


def filter_by_namespace(
    taskfiles: list[Taskfile],
    pattern: str | None = None,
    regex: str | None = None,
) -> list[SearchResult]:
    """Filter taskfiles by namespace name.

    Args:
        taskfiles: List of (namespace, tasks) tuples
        pattern: Optional pattern for substring matching
        regex: Optional regex pattern for matching

    Returns:
        List of search results for matching namespaces
    """
    results: list[SearchResult] = []

    for namespace, tasks in taskfiles:
        # If namespace matches, include all tasks from that namespace
        if matches_filters(namespace, pattern, regex):
            for group, task_name, description in tasks:
                results.append((namespace, group, task_name, description, "namespace"))

    return results


def filter_by_group(
    taskfiles: list[Taskfile],
    pattern: str | None = None,
    regex: str | None = None,
) -> list[SearchResult]:
    """Filter tasks by group name.

    Args:
        taskfiles: List of (namespace, tasks) tuples
        pattern: Optional pattern for substring matching
        regex: Optional regex pattern for matching

    Returns:
        List of search results for tasks in matching groups
    """
    results: list[SearchResult] = []

    for namespace, tasks in taskfiles:
        for group, task_name, description in tasks:
            if matches_filters(group, pattern, regex):
                results.append((namespace, group, task_name, description, "group"))

    return results


def filter_by_task(
    taskfiles: list[Taskfile],
    pattern: str | None = None,
    regex: str | None = None,
) -> list[SearchResult]:
    """Filter tasks by task name.

    Args:
        taskfiles: List of (namespace, tasks) tuples
        pattern: Optional pattern for substring matching
        regex: Optional regex pattern for matching

    Returns:
        List of search results for matching tasks
    """
    results: list[SearchResult] = []

    for namespace, tasks in taskfiles:
        for group, task_name, description in tasks:
            if matches_filters(task_name, pattern, regex):
                results.append((namespace, group, task_name, description, "task"))

    return results


def search_taskfiles(
    taskfiles: list[Taskfile],
    pattern: str | None = None,
    regex: str | None = None,
) -> list[SearchResult]:
    """Search across namespaces, groups, and task names.

    Searches in order: namespace → group → task.
    Results are deduplicated (a task only appears once even if it matches multiple criteria).

    Args:
        taskfiles: List of (namespace, tasks) tuples
        pattern: Optional pattern for substring matching
        regex: Optional regex pattern for matching

    Returns:
        List of unique search results with match context
    """
    # If no filters provided, return empty results
    if not pattern and not regex:
        return []

    # Collect all matches from different search types
    all_results: list[SearchResult] = []

    # Search by namespace (highest priority)
    all_results.extend(filter_by_namespace(taskfiles, pattern, regex))

    # Search by group
    all_results.extend(filter_by_group(taskfiles, pattern, regex))

    # Search by task name
    all_results.extend(filter_by_task(taskfiles, pattern, regex))

    # Deduplicate results while preserving order
    # Use (namespace, task_name) as unique key
    seen: set[tuple[str, str]] = set()
    unique_results: list[SearchResult] = []

    for namespace, group, task_name, description, match_type in all_results:
        key = (namespace, task_name)
        if key not in seen:
            seen.add(key)
            unique_results.append((namespace, group, task_name, description, match_type))

    return unique_results
