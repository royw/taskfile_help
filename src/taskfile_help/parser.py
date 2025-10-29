from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import re

from taskfile_help.output import Outputter
from taskfile_help.validator import validate_taskfile


# Compiled regex patterns for better performance
_GROUP_PATTERN = re.compile(r"\s*#\s*===\s*(.+?)\s*===")
_TASK_PATTERN = re.compile(r"^  ([a-zA-Z0-9_:-]+):\s*$")
_DESC_PATTERN = re.compile(r"^    desc:\s*(.+)$")
_INTERNAL_PATTERN = re.compile(r"^    internal:\s*true")


def _extract_group_name(line: str) -> str | None:
    """Extract group name from a group marker comment.
    The group marker is "# === Group Name ===".
    Returns None if a group marker is not found.
    """
    match = _GROUP_PATTERN.match(line)
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


def parse_taskfile(filepath: Path, namespace: str, outputter: Outputter) -> list[tuple[str, str, str]]:
    """
    Parse a Taskfile and extract public tasks with their descriptions and groups.

    This parser performs line-by-line parsing of the Taskfile YAML file.
    It is not a YAML parser, but rather a simple parser that looks for specific
    patterns in the file.

    This preserves the order of group comments and tasks as they appear in the file.

    Args:
        filepath: Path to the Taskfile YAML
        namespace: The namespace prefix (e.g., 'rag', 'dev')

    Returns:
        List of (group, task_name, description) tuples
    """
    tasks: list[tuple[str, str, str]] = []
    current_group = "Other"
    current_task = None
    current_desc = None
    is_internal = False
    in_tasks_section = False

    with taskfile_lines(filepath, outputter) as lines:
        # Validate YAML structure
        validate_taskfile(lines, outputter)

        for line in lines:
            # Check if we're in the tasks section
            if line.strip() == "tasks:":
                in_tasks_section = True
                continue

            if not in_tasks_section:
                continue

            # Check for group marker
            group_name = _extract_group_name(line)
            if group_name:
                _save_task_if_valid(tasks, current_group, current_task, current_desc, is_internal)
                current_group = group_name
                current_task = None
                current_desc = None
                is_internal = False
                continue

            # Check for task definition
            task_name = _extract_task_name(line)
            if task_name:
                _save_task_if_valid(tasks, current_group, current_task, current_desc, is_internal)
                current_task = task_name
                current_desc = None
                is_internal = False
                continue

            # If tracking a task, look for desc and internal flags
            if current_task:
                desc = _extract_description(line)
                if desc:
                    current_desc = desc
                    continue

                if _is_internal_task(line):
                    is_internal = True
                    continue

    # Save the last task
    _save_task_if_valid(tasks, current_group, current_task, current_desc, is_internal)

    return tasks
