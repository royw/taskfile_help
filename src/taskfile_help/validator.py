"""Taskfile validation module."""

from typing import Any

import yaml

from .output import Outputter


def _validate_task_field(
    task_name: str,
    field_name: str,
    expected_type: type | tuple[type, ...],
    task_def: dict[str, Any],
    outputter: Outputter,
) -> bool:
    """Validate a single task field type.

    Args:
        task_name: Name of the task being validated
        field_name: Name of the field to validate
        expected_type: Expected type(s) for the field
        task_def: Task definition dictionary
        outputter: Output handler for warnings

    Returns:
        True if field is valid or not present, False if invalid
    """
    if field_name not in task_def:
        return True

    if not isinstance(task_def[field_name], expected_type):
        # Format expected type name(s) with user-friendly names
        type_map = {
            "str": "string",
            "bool": "boolean",
            "int": "integer",
            "float": "float",
            "list": "list",
            "dict": "dictionary",
        }

        if isinstance(expected_type, tuple):
            type_names = " or ".join(type_map.get(t.__name__, t.__name__) for t in expected_type)
        else:
            type_names = type_map.get(expected_type.__name__, expected_type.__name__)

        actual_type_name = type(task_def[field_name]).__name__
        actual_type = type_map.get(actual_type_name, actual_type_name)

        outputter.output_warning(f"Task '{task_name}': '{field_name}' must be a {type_names}, got {actual_type}")
        return False

    return True


def _validate_task_fields(task_name: str, task_def: dict[str, Any], outputter: Outputter) -> bool:
    # Validate task fields
    valid = True
    valid &= _validate_task_field(task_name, "desc", str, task_def, outputter)
    valid &= _validate_task_field(task_name, "internal", bool, task_def, outputter)
    valid &= _validate_task_field(task_name, "cmds", (list, str), task_def, outputter)
    valid &= _validate_task_field(task_name, "deps", list, task_def, outputter)
    return valid


def _validate_version(data: dict[str, Any], outputter: Outputter) -> bool:
    """Validate version field."""
    if "version" not in data:
        outputter.output_warning("Missing 'version' field")
        return False
    if data["version"] != "3":
        outputter.output_warning(f"Invalid version '{data['version']}', expected '3'")
        return False
    return True


def _validate_tasks_section_exists(data: dict[str, Any], outputter: Outputter) -> bool:
    """Validate tasks section exists and is a dictionary."""
    if "tasks" not in data:
        outputter.output_warning("Missing 'tasks' section")
        return False
    if not isinstance(data["tasks"], dict):
        outputter.output_warning(f"'tasks' must be a dictionary, got {type(data['tasks']).__name__}")
        return False
    return True


def _validate_individual_tasks(tasks: dict[str, Any], outputter: Outputter) -> bool:
    valid = True
    for task_name, task_def in tasks.items():
        if not isinstance(task_def, dict):
            outputter.output_warning(f"Task '{task_name}' must be a dictionary")
            valid = False
            continue

        valid &= _validate_task_fields(task_name, task_def, outputter)

    return valid


def validate_taskfile(lines: list[str], outputter: Outputter) -> bool:
    """Validate Taskfile structure.

    Args:
        lines: Lines from the Taskfile
        outputter: Output handler for warnings

    Returns:
        True if valid, False if warnings were issued
    """
    # Parse YAML
    try:
        data = yaml.safe_load("".join(lines))
    except yaml.YAMLError as e:
        outputter.output_warning(f"Taskfile is not parseable: {e}; continuing...")
        return False

    # Check root is dictionary
    if not isinstance(data, dict):
        outputter.output_warning(f"Root must be a dictionary, got {type(data).__name__}")
        return False

    # Validate version (non-fatal)
    valid = _validate_version(data, outputter)

    # Validate tasks section exists (fatal if missing)
    if not _validate_tasks_section_exists(data, outputter):
        return False

    # Validate individual tasks (non-fatal)
    valid &= _validate_individual_tasks(data["tasks"], outputter)

    return valid
