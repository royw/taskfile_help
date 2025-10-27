# Development Guide

This guide covers setting up a development environment and contributing to taskfile-help.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/royw/taskfile-help.git
cd taskfile-help

# Install with development dependencies using uv
uv sync --dev

# Or using pip
pip install -e ".[dev]"
```

### Development Dependencies

The project includes these development tools:

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **mypy**: Static type checking
- **ruff**: Linting and formatting
- **pylint**: Additional linting
- **pymarkdownlnt**: Markdown linting
- **deadcode**: Dead code detection
- **radon**: Code complexity analysis

## Project Structure

```
taskfile-help/
├── src/
│   └── taskfile_help/
│       ├── __init__.py
│       ├── __main__.py         # Module entry point
│       ├── taskfile_help.py    # Main entry point
│       ├── config.py            # Configuration management
│       ├── discovery.py         # Taskfile discovery
│       ├── parser.py            # Taskfile parsing
│       └── output.py            # Output formatting
├── tests/
│   ├── unit/                    # Unit tests
│   │   ├── test_config.py
│   │   ├── test_discovery.py
│   │   ├── test_output.py
│   │   ├── test_parser.py
│   │   └── test_taskfile_help.py
│   └── e2e/                     # End-to-end tests
│       └── test_cli.py
├── docs/                        # Documentation
├── pyproject.toml              # Project configuration
├── Taskfile.yml                # Development tasks
└── README.md
```

## Development Workflow

### Using Task (Recommended)

The project includes a Taskfile with common development tasks:

```bash
# Show available tasks
task help

# Run all checks (format, lint, test)
task make

# Format code
task format

# Run linters
task lint

# Run tests
task test

# Run tests with coverage
task test:coverage

# Build documentation
task docs:build

# Serve documentation locally
task docs:serve

# Build distribution packages
task build
```

### Manual Commands

If you prefer not to use Task:

```bash
# Format code
uv run ruff format src/
uv run ruff check --fix src/

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
uv run pylint src/

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/taskfile_help --cov-report=html

# Build package
uv build
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_parser.py

# Run specific test
uv run pytest tests/unit/test_parser.py::TestParseTaskfile::test_parse_simple_taskfile

# Run with coverage
uv run pytest --cov=src/taskfile_help --cov-report=html

# Run only unit tests
uv run pytest tests/unit/

# Run only e2e tests
uv run pytest tests/e2e/
```

### Writing Tests

#### Unit Tests

```python
from pathlib import Path
import pytest
from taskfile_help.parser import parse_taskfile
from taskfile_help.output import TextOutputter

def test_parse_simple_taskfile(tmp_path: Path) -> None:
    """Test parsing a simple Taskfile."""
    taskfile = tmp_path / "Taskfile.yml"
    taskfile.write_text("""version: '3'

tasks:
  build:
    desc: Build the project
    cmds:
      - echo "Building..."
""")
    
    outputter = TextOutputter()
    tasks = parse_taskfile(taskfile, "", outputter)
    
    assert len(tasks) == 1
    assert tasks[0] == ("Other", "build", "Build the project")
```

#### End-to-End Tests

```python
import subprocess
import sys

def test_help_command() -> None:
    """Test that help command works."""
    result = subprocess.run(
        [sys.executable, "-m", "taskfile_help", "-h"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Dynamic Taskfile help generator" in result.stdout
```

### Test Coverage

Aim for >90% code coverage. Check coverage report:

```bash
uv run pytest --cov=src/taskfile_help --cov-report=html
open htmlcov/index.html
```

## Code Style

### Formatting

The project uses **ruff** for formatting:

```bash
# Format code
uv run ruff format src/

# Check formatting
uv run ruff format --check src/
```

### Linting

Multiple linters ensure code quality:

```bash
# Ruff (fast Python linter)
uv run ruff check src/

# MyPy (type checking)
uv run mypy src/

# Pylint (additional checks)
uv run pylint src/
```

### Type Hints

All code must include type hints:

```python
def parse_taskfile(
    filepath: Path,
    namespace: str,
    outputter: Outputter
) -> list[tuple[str, str, str]]:
    """Parse a Taskfile and extract tasks."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def find_taskfile(search_dirs: list[Path]) -> Path | None:
    """Find a Taskfile in the given search directories.

    Args:
        search_dirs: List of directories to search

    Returns:
        Path to the Taskfile if found, None otherwise

    Raises:
        ValueError: If search_dirs is empty
    """
    ...
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

### 2. Make Changes

- Write code following style guidelines
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Run Checks

```bash
# Run all checks
task make

# Or manually:
task format
task lint
task test
```

### 4. Commit Changes

```bash
git add .
git commit -m "Add feature: description"
```

Use conventional commit messages:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a pull request on GitHub.

## Debugging

### Using Print Statements

```python
# Temporary debugging
print(f"DEBUG: tasks = {tasks}")

# Use outputter for consistent output
outputter.output_message(f"DEBUG: {value}")
```

### Using Python Debugger

```python
import pdb; pdb.set_trace()
```

### Running with Verbose Output

```bash
taskfile-help --verbose
```

## Documentation

### Building Documentation

```bash
# Build docs
task docs:build

# Serve docs locally
task docs:serve

# Open in browser
open http://127.0.0.1:8000
```

### Writing Documentation

- Use Markdown for all documentation
- Include code examples
- Add diagrams where helpful (Mermaid supported)
- Keep language clear and concise

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run all tests: `task make`
4. Build package: `task build`
5. Create git tag: `git tag v0.2.0`
6. Push tag: `git push origin v0.2.0`
7. Create GitHub release
8. Publish to PyPI: `uv publish`

## Getting Help

- Check existing issues on GitHub
- Review documentation
- Ask questions in discussions
- Join community chat (if available)

## Code Review Guidelines

When reviewing PRs:

- Check code style and formatting
- Verify tests are included
- Ensure documentation is updated
- Test functionality locally
- Provide constructive feedback
