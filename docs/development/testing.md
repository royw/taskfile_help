# Testing

Comprehensive testing guide for taskfile-help.

## Test Structure

```text
tests/
├── unit/                    # Unit tests
│   ├── test_config.py
│   ├── test_discovery.py
│   ├── test_output.py
│   ├── test_parser.py
│   └── test_taskfile_help.py
└── e2e/                     # End-to-end tests
    └── test_cli.py
```

## Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/test_parser.py

# Specific test
uv run pytest tests/unit/test_parser.py::TestParseTaskfile::test_parse_simple_taskfile

# With coverage
uv run pytest --cov=src/taskfile_help --cov-report=html

# Only unit tests
uv run pytest tests/unit/

# Only e2e tests
uv run pytest tests/e2e/
```

## Test Coverage

Current coverage: **95%**

View coverage report:

```bash
uv run pytest --cov=src/taskfile_help --cov-report=html
open htmlcov/index.html
```

## Writing Tests

### Unit Test Example

```python
from pathlib import Path
import pytest
from taskfile_help.parser import parse_taskfile
from taskfile_help.output import TextOutputter

def test_parse_simple_taskfile(tmp_path: Path) -> None:
    """Test parsing a simple Taskfile."""
    taskfile = tmp_path / "Taskfile.yml"
    taskfile.write_text(\"\"\"version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
\"\"\")
    
    outputter = TextOutputter()
    tasks = parse_taskfile(taskfile, "", outputter)
    
    assert len(tasks) == 1
    assert tasks[0] == ("Other", "build", "Build the project")
```

### E2E Test Example

```python
import subprocess
import sys

def test_help_command() -> None:
    \"\"\"Test that help command works.\"\"\"
    result = subprocess.run(
        [sys.executable, "-m", "taskfile_help", "-h"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Dynamic Taskfile help generator" in result.stdout
```

## Test Fixtures

Common fixtures available:

- `tmp_path`: Temporary directory
- `monkeypatch`: Modify environment
- `capsys`: Capture stdout/stderr

## Best Practices

1. **Test one thing**: Each test should verify one behavior
2. **Use descriptive names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Clean up**: Use fixtures for setup/teardown
5. **Mock external dependencies**: Keep tests isolated
