# Installation

## Requirements

- Python 3.11 or higher
- No external dependencies (uses only Python standard library)

## Install from PyPI

```bash
pip install taskfile-help
```

## Install from Source

Clone the repository and install:

```bash
git clone https://github.com/royw/taskfile-help.git
cd taskfile-help
pip install .
```

## Development Installation

For development, install with dev dependencies:

```bash
git clone https://github.com/royw/taskfile-help.git
cd taskfile-help
uv sync --dev
```

Or using pip:

```bash
pip install -e ".[dev]"
```

## Verify Installation

Check that the installation was successful:

```bash
taskfile-help --help
```

You should see the help message with all available options.

## Alternative Invocation Methods

You can invoke taskfile-help in several ways:

### Console Script (Recommended)

```bash
taskfile-help
```

### Python Module

```bash
python -m taskfile_help
```

### Direct Python Import

```python
from taskfile_help.taskfile_help import main
import sys

sys.exit(main())
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade taskfile-help
```

## Uninstalling

To remove taskfile-help:

```bash
pip uninstall taskfile-help
```
