# Taskfile Validation Implementation Plan

## Overview

Add YAML validation to ensure Taskfiles conform to Task version 3 specification. Validation runs automatically on every parse with warnings for issues but continues processing.

## Requirements

- **Always enabled**: No opt-in flag required
- **Non-fatal**: Validation errors produce warnings, processing continues
- **Version check**: Must validate `version: '3'`
- **Structure validation**: Check required fields and types
- **Helpful messages**: Clear warnings about what's wrong and where

## Implementation Checklist

### Phase 1: Core Validation

- [ ] Add `pyyaml` dependency to `pyproject.toml`
- [ ] Create `src/taskfile_help/validator.py` module
- [ ] Implement `validate_taskfile(data: dict, filepath: Path, outputter: Outputter) -> bool`
  - [ ] Check root is a dictionary
  - [ ] Check `version` field exists
  - [ ] Check `version` equals `'3'` (string comparison)
  - [ ] Check `tasks` section exists
  - [ ] Check `tasks` is a dictionary
  - [ ] Return True if valid, False if warnings issued

### Phase 2: Integration with Parser

- [ ] Modify `parse_taskfile()` in `parser.py`:
  - [ ] Read file content once
  - [ ] Parse YAML with `yaml.safe_load()`
  - [ ] Call `validate_taskfile()` before line-by-line parsing
  - [ ] Continue with existing line-by-line logic regardless of validation result
  - [ ] Handle `yaml.YAMLError` exceptions gracefully

### Phase 3: Detailed Task Validation

- [ ] Validate individual task structure:
  - [ ] Task names are valid (alphanumeric, hyphens, underscores, colons)
  - [ ] Task values are dictionaries
  - [ ] `desc` field is a string (if present)
  - [ ] `internal` field is boolean (if present)
  - [ ] `cmds` field is list or string (if present)
  - [ ] `deps` field is list (if present)

### Phase 4: Warning Messages

- [ ] Implement clear warning messages:
  - [ ] `Warning: {filepath} is not parseable: {reason}; continuing...`
  - [ ] `Warning: {filepath}: Missing 'version' field`
  - [ ] `Warning: {filepath}: Invalid version '{version}', expected '3'`
  - [ ] `Warning: {filepath}: Missing 'tasks' section`
  - [ ] `Warning: {filepath}: 'tasks' must be a dictionary, got {type}`
  - [ ] `Warning: {filepath}: Task '{task}' has invalid structure`

### Phase 5: Testing

- [ ] Unit tests for `validator.py`:
  - [ ] Test valid Taskfile passes
  - [ ] Test missing version field
  - [ ] Test wrong version (e.g., '2', '3.0', 3)
  - [ ] Test missing tasks section
  - [ ] Test invalid tasks type (list, string, etc.)
  - [ ] Test invalid YAML syntax
  - [ ] Test malformed task definitions

- [ ] Integration tests:
  - [ ] Test validation warnings appear in output
  - [ ] Test parsing continues after validation warnings
  - [ ] Test valid Taskfile produces no warnings

- [ ] E2E tests:
  - [ ] Test CLI with invalid Taskfile shows warnings
  - [ ] Test CLI continues to show tasks despite warnings

### Phase 6: Documentation

- [ ] Update `README.md`:
  - [ ] Document validation behavior
  - [ ] Show example warning messages

- [ ] Update `docs/setup/configuration.md`:
  - [ ] Add "Validation" section
  - [ ] Explain version 3 requirement

- [ ] Update `docs/development/architecture.md`:
  - [ ] Document validator module
  - [ ] Update validation section with implementation details

## Code Structure

```
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


def validate_taskfile(data: Any, filepath: Path, outputter: Outputter) -> bool:
    """Validate Taskfile structure.
    
    Args:
        data: Parsed YAML data
        filepath: Path to Taskfile
        outputter: Output handler for warnings
        
    Returns:
        True if valid, False if warnings were issued
    """
    valid = True
    
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
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        outputter.output_error(f"Error reading {filepath}: {e}")
        return []
    
    # Validate YAML structure
    try:
        data = yaml.safe_load(content)
        validate_taskfile(data, filepath, outputter)
    except yaml.YAMLError as e:
        outputter.output_warning(
            f"{filepath} is not parseable: {e}; continuing..."
        )
    
    # Continue with line-by-line parsing (existing logic)
    lines = content.splitlines(keepends=True)
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
