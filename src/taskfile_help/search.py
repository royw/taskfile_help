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


def matches_all_patterns(text: str, patterns: list[str]) -> bool:
    """Check if text matches all patterns using case-insensitive substring match.

    Args:
        text: Text to search in
        patterns: List of patterns to search for (all must match)

    Returns:
        True if all patterns are found in text (case-insensitive), False otherwise
    """
    return all(pattern.lower() in text.lower() for pattern in patterns)


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


def matches_all_regexes(text: str, regexes: list[str]) -> bool:
    """Check if text matches all regex patterns.

    Args:
        text: Text to search in
        regexes: List of regex patterns to search for (all must match)

    Returns:
        True if all regexes match text, False otherwise
    """
    return all(matches_regex(text, regex) for regex in regexes)


def task_matches_filters(
    namespace: str,
    group: str,
    task_name: str,
    description: str,
    patterns: list[str] | None = None,
    regexes: list[str] | None = None,
) -> bool:
    """Check if a task matches all patterns and regexes.

    Patterns and regexes are checked against the combined text of:
    namespace, group, task_name, and description.

    Args:
        namespace: Task namespace
        group: Task group
        task_name: Task name
        description: Task description
        patterns: List of patterns (all must match)
        regexes: List of regexes (all must match)

    Returns:
        True if all patterns and regexes match, False otherwise
    """
    # Combine all searchable fields
    combined = f"{namespace} {group} {task_name} {description}"

    # Check all patterns match
    if patterns and not matches_all_patterns(combined, patterns):
        return False

    # Check all regexes match and return result
    return not (regexes and not matches_all_regexes(combined, regexes))


def search_taskfiles(
    taskfiles: list[Taskfile],
    patterns: list[str] | None = None,
    regexes: list[str] | None = None,
) -> list[SearchResult]:
    """Search across namespaces, groups, task names, and descriptions.

    All patterns and regexes must match somewhere in the combined text of:
    namespace, group, task_name, and description.

    Args:
        taskfiles: List of (namespace, tasks) tuples
        patterns: List of patterns for substring matching (all must match)
        regexes: List of regexes for pattern matching (all must match)

    Returns:
        List of search results for matching tasks
    """
    # At least one pattern or regex is required
    if not patterns and not regexes:
        return []

    results: list[SearchResult] = []

    for namespace, tasks in taskfiles:
        for group, task_name, description in tasks:
            if task_matches_filters(namespace, group, task_name, description, patterns=patterns, regexes=regexes):
                results.append((namespace, group, task_name, description, "match"))

    return results
