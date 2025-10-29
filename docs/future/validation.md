# Taskfile Validation Implementation Plan

## Overview

Add YAML validation to ensure Taskfiles conform to Task version 3 specification. Validation runs automatically
on every parse with warnings for issues but continues processing.

## Requirements

- **Always enabled**: No opt-in flag required
- **Non-fatal**: Validation errors produce warnings, processing continues
- **Version check**: Must validate `version: '3'`
- **Structure validation**: Check required fields and types
- **Helpful messages**: Clear warnings about what's wrong and where

## Implementation Checklist

### Phase 1: Core Validation

- [x] Add `pyyaml` dependency to `pyproject.toml` using `uv add pyyaml`
- [x] Create `src/taskfile_help/validator.py` module
- [x] Implement `validate_taskfile(lines: list[str], outputter: Outputter) -> bool`
  - [x] Parse YAML with `yaml.safe_load()`
  - [x] Check root is a dictionary
  - [x] Check `version` field exists
  - [x] Check `version` equals `'3'` (string comparison)
  - [x] Check `tasks` section exists
  - [x] Check `tasks` is a dictionary
  - [x] Validate individual task structure:
    - [ ] Task names are valid (alphanumeric, hyphens, underscores, colons)
    - [x] Task values are dictionaries
    - [x] `desc` field is a string (if present)
    - [x] `internal` field is boolean (if present)
    - [x] `cmds` field is list or string (if present)
    - [x] `deps` field is list (if present)
  - [x] Implement clear warning messages:
    - [x] `Warning: {filepath} is not parseable: {reason}; continuing...`
    - [x] `Warning: {filepath}: Missing 'version' field`
    - [x] `Warning: {filepath}: Invalid version '{version}', expected '3'`
    - [x] `Warning: {filepath}: Missing 'tasks' section`
    - [x] `Warning: {filepath}: 'tasks' must be a dictionary, got {type}`
    - [x] `Warning: {filepath}: Task '{task}' has invalid structure`
  - [x] Handle `yaml.YAMLError` exceptions gracefully
  - [x] Return True if valid, False if warnings issued

### Phase 2: Integration with Parser

- [x] Modify `parse_taskfile()` in `parser.py`:
  - [x] Read file content once into lines
  - [x] Call `validate_taskfile(lines, outputter)` before line-by-line parsing
  - [x] Continue with existing line-by-line logic regardless of validation result

### Phase 3: Testing

- [x] Unit tests for `validator.py`:
  - [x] Test valid Taskfile passes
  - [x] Test missing version field
  - [x] Test wrong version (e.g., '2', '3.0', 3)
  - [x] Test missing tasks section
  - [x] Test invalid tasks type (list, string, etc.)
  - [x] Test invalid YAML syntax
  - [x] Test malformed task definitions

- [x] Integration tests:
  - [x] Test validation warnings appear in output
  - [x] Test parsing continues after validation warnings
  - [x] Test valid Taskfile produces no warnings

- [x] E2E tests:
  - [x] Test CLI with invalid Taskfile shows warnings
  - [x] Test CLI continues to show tasks despite warnings

### Phase 4: Documentation

- [x] Update `README.md`:
  - [x] Document validation behavior
  - [x] Show example warning messages

- [x] Update `docs/setup/configuration.md`:
  - [x] Add "Validation" section
  - [x] Explain version 3 requirement

- [x] Update `docs/development/architecture.md`:
  - [x] Document validator module
  - [x] Update validation section with implementation details

## Code Structure

```text
src/taskfile_help/
├── validator.py          # NEW: Validation logic
├── parser.py             # MODIFIED: Integrate validation
└── output.py             # EXISTING: Warning output

tests/
├── unit/
│   └── test_validator.py # NEW: Validator tests
└── e2e/
    └── test_cli.py       # MODIFIED: Add validation tests
```

## Example Implementation

### validator.py

```python
"""Taskfile validation module."""

from pathlib import Path
from typing import Any

from .output import Outputter


def validate_taskfile(lines: list[str], filepath: Path, outputter: Outputter) -> bool:
    """Validate Taskfile structure.
    
    Args:
        lines: Lines from the Taskfile
        filepath: Path to Taskfile
        outputter: Output handler for warnings
        
    Returns:
        True if valid, False if warnings were issued
    """
    valid = True
    
    # Parse YAML
    try:
        data = yaml.safe_load(''.join(lines))
    except yaml.YAMLError as e:
        outputter.output_warning(
            f"{filepath} is not parseable: {e}; continuing..."
        )
        return False
    
    # Check root is dictionary
    if not isinstance(data, dict):
        outputter.output_warning(
            f"{filepath}: Root must be a dictionary, got {type(data).__name__}"
        )
        return False
    
    # Check version field
    if 'version' not in data:
        outputter.output_warning(f"{filepath}: Missing 'version' field")
        valid = False
    elif data['version'] != '3':
        outputter.output_warning(
            f"{filepath}: Invalid version '{data['version']}', expected '3'"
        )
        valid = False
    
    # Check tasks section
    if 'tasks' not in data:
        outputter.output_warning(f"{filepath}: Missing 'tasks' section")
        return False
    
    if not isinstance(data['tasks'], dict):
        outputter.output_warning(
            f"{filepath}: 'tasks' must be a dictionary, got {type(data['tasks']).__name__}"
        )
        return False
    
    # Validate individual tasks
    for task_name, task_def in data['tasks'].items():
        if not isinstance(task_def, dict):
            outputter.output_warning(
                f"{filepath}: Task '{task_name}' must be a dictionary"
            )
            valid = False
    
    return valid
```

### Modified parser.py

```python
import yaml
from .validator import validate_taskfile

def parse_taskfile(filepath: Path, namespace: str, outputter: Outputter) -> list[tuple[str, str, str]]:
    """Parse a Taskfile and extract public tasks with their descriptions."""
    
    # Read file
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as e:
        outputter.output_error(f"Error reading {filepath}: {e}")
        return []
    
    # Validate YAML structure
    validate_taskfile(lines, filepath, outputter)
    
    # Continue with line-by-line parsing (existing logic)
    # ... rest of existing implementation
```

## Performance Impact

- **Minimal**: YAML parsing adds ~1-2ms per file
- **Acceptable**: Validation is fast and runs once per file
- **Cached**: File already read into memory, no extra I/O

## Dependencies

- Add to `pyproject.toml`:

  ```toml
  dependencies = [
      "pyyaml>=6.0",
  ]
  ```

## Success Criteria

- [ ] All Taskfiles are validated automatically
- [ ] Invalid Taskfiles show clear warnings
- [ ] Processing continues after validation warnings
- [ ] Version 3 requirement is enforced
- [ ] No performance degradation (< 5ms overhead)
- [ ] 100% test coverage for validator module
- [ ] Documentation updated
