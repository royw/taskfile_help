from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import re

from taskfile_help.output import Outputter
from taskfile_help.validator import validate_taskfile


# Compiled regex patterns for better performance
_TASK_PATTERN = re.compile(r"^  ([a-zA-Z0-9_:-]+):\s*$")
_DESC_PATTERN = re.compile(r"^    desc:\s*(.+)$")
_INTERNAL_PATTERN = re.compile(r"^    internal:\s*true")


@dataclass
class _ParserState:
    """State for parsing a Taskfile."""

    current_group: str = "Other"
    current_task: str | None = None
    current_desc: str | None = None
    is_internal: bool = False
    in_tasks_section: bool = False

    def reset_task(self) -> None:
        """Reset task-specific state."""
        self.current_task = None
        self.current_desc = None
        self.is_internal = False

    def start_new_group(self, group_name: str) -> None:
        """Start tracking a new group."""
        self.current_group = group_name
        self.reset_task()

    def start_new_task(self, task_name: str) -> None:
        """Start tracking a new task."""
        self.current_task = task_name
        self.current_desc = None
        self.is_internal = False

    def handle_group_marker(self, group_name: str, tasks: list[tuple[str, str, str]]) -> None:
        """Handle a group marker line."""
        _save_task_if_valid(tasks, self.current_group, self.current_task, self.current_desc, self.is_internal)
        self.start_new_group(group_name)

    def handle_task_definition(self, task_name: str, tasks: list[tuple[str, str, str]]) -> None:
        """Handle a task definition line."""
        _save_task_if_valid(tasks, self.current_group, self.current_task, self.current_desc, self.is_internal)
        self.start_new_task(task_name)

    def handle_description(self, desc: str) -> None:
        """Handle a description line."""
        self.current_desc = desc

    def handle_internal_flag(self) -> None:
        """Handle an internal flag line."""
        self.is_internal = True


def _extract_group_name(line: str, group_pattern: re.Pattern[str]) -> str | None:
    """Extract group name from a group marker comment.
    The group marker is "# === Group Name ===" by default.
    Returns None if a group marker is not found.

    Args:
        line: Line to check for group marker
        group_pattern: Compiled regex pattern for group markers
    """
    match = group_pattern.match(line)
    return match.group(1).strip() if match else None


def _extract_task_name(line: str) -> str | None:
    """Extract task name from a task definition line.
    The task definition line is of the form "task-name:"
    Returns None if a task name is not found.
    """
    match = _TASK_PATTERN.match(line)
    return match.group(1) if match else None


def _extract_description(line: str) -> str | None:
    """Extract description from a desc line.
    The desc line is of the form "    desc: Description".
    An empty description, "    desc:", is considered not found
    Returns None if a description is not found.
    """
    match = _DESC_PATTERN.match(line)
    return match.group(1).strip() if match else None


def _is_internal_task(line: str) -> bool:
    """Check if line marks task as internal.
    The internal line is of the form "    internal: true".
    Returns True if the line marks the task as internal, False otherwise.
    """
    return bool(_INTERNAL_PATTERN.match(line))


def _save_task_if_valid(
    tasks: list[tuple[str, str, str]],
    group: str,
    task_name: str | None,
    description: str | None,
    is_internal: bool,
) -> None:
    """Save task to list if it's valid and public.
    A task is valid if it has a name and description and is not internal.
    Valid tasks are added to the given tasks list.
    """
    if task_name and description and not is_internal:
        tasks.append((group, task_name, description))


def _try_handle_tasks_section_start(line: str, state: _ParserState) -> bool:
    """Check if line starts the tasks section."""
    if line.strip() == "tasks:":
        state.in_tasks_section = True
        return True
    return False


def _try_handle_group_marker(
    line: str,
    state: _ParserState,
    tasks: list[tuple[str, str, str]],
    group_pattern: re.Pattern[str],
) -> bool:
    """Check if line is a group marker and handle it.

    Args:
        line: Line to check
        state: Current parser state
        tasks: List of tasks
        group_pattern: Compiled regex pattern for group markers
    """
    group_name = _extract_group_name(line, group_pattern)
    if group_name:
        state.handle_group_marker(group_name, tasks)
        return True
    return False


def _try_handle_task_definition(line: str, state: _ParserState, tasks: list[tuple[str, str, str]]) -> bool:
    """Check if line is a task definition and handle it."""
    task_name = _extract_task_name(line)
    if task_name:
        state.handle_task_definition(task_name, tasks)
        return True
    return False


def _try_handle_task_properties(line: str, state: _ParserState) -> bool:
    """Check if line is a task property (desc or internal) and handle it."""
    if not state.current_task:
        return False

    desc = _extract_description(line)
    if desc:
        state.handle_description(desc)
        return True

    if _is_internal_task(line):
        state.handle_internal_flag()
        return True

    return False


def _process_line(
    line: str,
    state: _ParserState,
    tasks: list[tuple[str, str, str]],
    group_pattern: re.Pattern[str],
) -> None:
    """Process a single line of the Taskfile.

    Args:
        line: Line to process
        state: Current parser state
        tasks: List to append completed tasks to
        group_pattern: Compiled regex pattern for group markers
    """
    # Try each handler in order until one succeeds
    if _try_handle_tasks_section_start(line, state):
        return

    if not state.in_tasks_section:
        return

    if _try_handle_group_marker(line, state, tasks, group_pattern):
        return

    if _try_handle_task_definition(line, state, tasks):
        return

    _try_handle_task_properties(line, state)


@contextmanager
def taskfile_lines(filepath: Path, outputter: Outputter) -> Generator[list[str], None, None]:
    """Context manager to read lines from a taskfile.

    Args:
        filepath: Path to the taskfile
        outputter: Outputter instance for error messages

    Yields:
        List of lines from the file, or empty list on error
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            yield f.readlines()
    except (OSError, UnicodeDecodeError) as e:
        outputter.output_error(f"Error reading {filepath}: {e}")
        yield []


def parse_taskfile(
    filepath: Path,
    namespace: str,
    outputter: Outputter,
    group_pattern: str = r"\s*#\s*===\s*(.+?)\s*===",
) -> list[tuple[str, str, str]]:
    """
    Parse a Taskfile and extract public tasks with their descriptions and groups.

    This parser performs line-by-line parsing of the Taskfile YAML file.
    It is not a YAML parser, but rather a simple parser that looks for specific
    patterns in the file.

    This preserves the order of group comments and tasks as they appear in the file.

    Args:
        filepath: Path to the Taskfile YAML
        namespace: The namespace prefix (e.g., 'rag', 'dev')
        outputter: Outputter instance for error messages
        group_pattern: Regular expression pattern for group markers (default: r"\\s*#\\s*===\\s*(.+?)\\s*===")

    Returns:
        List of (group, task_name, description) tuples
    """
    tasks: list[tuple[str, str, str]] = []
    state = _ParserState()
    compiled_group_pattern = re.compile(group_pattern)

    with taskfile_lines(filepath, outputter) as lines:
        # Validate YAML structure
        validate_taskfile(lines, outputter)

        # Process each line
        for line in lines:
            _process_line(line, state, tasks, compiled_group_pattern)

    # Save the last task
    _save_task_if_valid(tasks, state.current_group, state.current_task, state.current_desc, state.is_internal)

    return tasks
