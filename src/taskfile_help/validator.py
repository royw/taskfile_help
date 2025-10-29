"""Taskfile validation module."""

from pathlib import Path
from typing import Any

import yaml

from .output import Outputter


def validate_taskfile(lines: list[str], outputter: Outputter) -> bool:
    """Validate Taskfile structure.

    Args:
        lines: Lines from the Taskfile
        outputter: Output handler for warnings

    Returns:
        True if valid, False if warnings were issued
    """
    valid = True

    # Parse YAML
    try:
        data = yaml.safe_load("".join(lines))
    except yaml.YAMLError as e:
        outputter.output_warning(f"Taskfile is not parseable: {e}; continuing...")
        return False

    # Check root is dictionary
    if not isinstance(data, dict):
        outputter.output_warning(
            f"Root must be a dictionary, got {type(data).__name__}"
        )
        return False

    # Check version field
    if "version" not in data:
        outputter.output_warning("Missing 'version' field")
        valid = False
    elif data["version"] != "3":
        outputter.output_warning(
            f"Invalid version '{data['version']}', expected '3'"
        )
        valid = False

    # Check tasks section
    if "tasks" not in data:
        outputter.output_warning("Missing 'tasks' section")
        return False

    if not isinstance(data["tasks"], dict):
        outputter.output_warning(
            f"'tasks' must be a dictionary, got {type(data['tasks']).__name__}"
        )
        return False

    # Validate individual tasks
    for task_name, task_def in data["tasks"].items():
        if not isinstance(task_def, dict):
            outputter.output_warning(f"Task '{task_name}' must be a dictionary")
            valid = False
            continue

        # Validate task fields
        if "desc" in task_def and not isinstance(task_def["desc"], str):
            outputter.output_warning(
                f"Task '{task_name}': 'desc' must be a string, got {type(task_def['desc']).__name__}"
            )
            valid = False

        if "internal" in task_def and not isinstance(task_def["internal"], bool):
            outputter.output_warning(
                f"Task '{task_name}': 'internal' must be a boolean, got {type(task_def['internal']).__name__}"
            )
            valid = False

        if "cmds" in task_def and not isinstance(task_def["cmds"], (list, str)):
            outputter.output_warning(
                f"Task '{task_name}': 'cmds' must be a list or string, got {type(task_def['cmds']).__name__}"
            )
            valid = False

        if "deps" in task_def and not isinstance(task_def["deps"], list):
            outputter.output_warning(
                f"Task '{task_name}': 'deps' must be a list, got {type(task_def['deps']).__name__}"
            )
            valid = False

    return valid
