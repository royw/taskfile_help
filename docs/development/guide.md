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

# Install git hooks (optional but recommended)
task git:hooks:install
```

### Git Hooks

The project uses git hooks to enforce commit standards and automate CHANGELOG updates.

#### Installation

```bash
# Install hooks (recommended for all contributors)
task git:hooks:install

# Uninstall hooks
task git:hooks:uninstall

# Test hooks
task git:hooks:test
```

#### Available Hooks

**commit-msg** - Enforces conventional commit format:

- Validates commit messages before commit is created
- Rejects invalid messages with helpful error
- Ensures all commits follow project standards

**post-commit** - Automates CHANGELOG updates:

- Parses conventional commit messages
- Adds entries to appropriate CHANGELOG sections
- Amends commit to include CHANGELOG changes

#### Conventional Commits

All commits must follow the conventional commit format:

```text
<type>: <description>
```

**Supported types:**

- `feat:` - New feature (added to CHANGELOG)
- `fix:` - Bug fix (added to CHANGELOG)
- `docs:` - Documentation changes (added to CHANGELOG)
- `refactor:` - Code refactoring (added to CHANGELOG)
- `perf:` - Performance improvements (added to CHANGELOG)
- `test:` - Test-related changes
- `chore:` - Maintenance tasks
- `style:` - Code style/formatting
- `ci:` - CI/CD changes
- `build:` - Build system changes
- `revert:` - Revert previous commits

**Examples:**

```bash
git commit -m "feat: add shell auto-completion support"
git commit -m "fix: resolve memory leak in parser"
git commit -m "docs: update installation guide"
git commit -m "test: add edge case tests for discovery"
```

See [.githooks/README.md](../../.githooks/README.md) for complete documentation.

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

```text
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

E2E tests can use two approaches:

##### **Direct `main()` calls** (preferred for most tests)

- Simpler and faster
- Easier to inject dependencies and mock behavior
- Better for testing application logic

```python
from taskfile_help.taskfile_help import main
from unittest.mock import patch

def test_main_taskfile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main taskfile display."""
    taskfile = tmp_path / "Taskfile.yml"
    taskfile.write_text("""version: '3'
tasks:
  build:
    desc: Build the project
""")
    monkeypatch.chdir(tmp_path)
    
    with patch("sys.stdout.isatty", return_value=False):
        result = main(["taskfile-help"])
    
    assert result == 0
```

##### **Subprocess calls** (for external access testing)

- Tests actual installed scripts and module invocation
- Validates package installation and entry points
- Use for testing: `python -m taskfile_help`, console scripts, etc.

```python
import subprocess
import sys

def test_module_invocation() -> None:
    """Test that module can be invoked with -m flag."""
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
uv run ruff check --fix --select I src/
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

All code must include modern type hints (at least what python 3.11 supports (PEP 484, 563, 585, 604, 673, 646)):

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

## CHANGELOG Maintenance

The project uses automated CHANGELOG updates via git hooks.

### Automatic Updates

When you commit with a conventional commit message, the post-commit hook automatically:

1. Parses your commit message
2. Adds an entry to the appropriate section in `CHANGELOG.md`
3. Amends your commit to include the CHANGELOG update

**Example workflow:**

```bash
# Make your changes
git add src/taskfile_help/parser.py

# Commit with conventional format
git commit -m "feat: add dependency parsing support"

# Hook automatically updates CHANGELOG.md:
#   ### Added
#   - add dependency parsing support (abc123)
```

### CHANGELOG Structure

The `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) format:

- **[Unreleased]** - Current development work (auto-updated by hooks)
  - **Added** - New features (`feat:` commits)
  - **Changed** - Changes in existing functionality (`docs:`, `refactor:`, `perf:` commits)
  - **Fixed** - Bug fixes (`fix:` commits)
- **[Version]** - Released versions with date

### Manual Updates

You can manually edit `CHANGELOG.md` when needed:

- Reorganizing entries for clarity
- Adding breaking changes notes
- Preparing for a release
- Adding migration guides

### Release Process

When releasing a new version:

1. Move entries from `[Unreleased]` to a new version section
2. Add the version number and date: `## [0.2.0] - 2025-10-28`
3. Update version links at the bottom of the file
4. Commit with: `chore: prepare release v0.2.0`

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

1. Run all tests: `task make`
2. Update and commit CHANGELOG.md
3. Update version in `task version:bump`
4. Create git tag: `task tag`
5. Push tag: `git push origin v0.2.0`
6. Create GitHub release
7. Publish to PyPI: `uv publish`

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
