# Architecture

taskfile-help is designed with simplicity and performance in mind. It uses a modular architecture with clear separation of concerns.

## Overview

```mermaid
graph TD
    A[CLI Entry Point] --> B[Config]
    B --> C[Discovery]
    B --> D[Outputter]
    C --> E[Parser]
    E --> F[Tasks]
    F --> D
    D --> G[Output]
```

## Components

### 1. Entry Point (`taskfile_help.py`)

The main entry point that orchestrates the application flow:

- Parses command-line arguments
- Initializes configuration
- Selects appropriate outputter
- Coordinates task discovery and parsing
- Handles error cases

**Key Function**: `main(argv: list[str] | None = None) -> int`

### 2. Configuration (`config.py`)

Manages application configuration from multiple sources:

- Command-line arguments (via `argparse`)
- `pyproject.toml` configuration file
- Default values

**Classes**:

- `Args`: Parsed command-line arguments
- `Config`: Combined configuration with derived values

**Features**:

- TTY detection for color support
- Search directory resolution
- Configuration priority handling

### 3. Discovery (`discovery.py`)

Handles Taskfile discovery across search paths:

- Finds main Taskfile (`Taskfile.yml` or `Taskfile.yaml`)
- Finds namespace Taskfiles (`Taskfile-<namespace>.yml`)
- Searches multiple directories
- Returns first match (priority-based)

**Class**: `TaskfileDiscovery`

**Methods**:

- `find_main_taskfile() -> Path | None`
- `find_namespace_taskfile(namespace: str) -> Path | None`
- `get_all_namespace_taskfiles() -> list[tuple[str, Path]]`
- `get_possible_paths(namespace: str) -> list[Path]`

### 4. Parser (`parser.py`)

Line-by-line Taskfile parser (not a full YAML parser):

- Extracts task names and descriptions
- Identifies group markers (`# === Group Name ===`)
- Detects internal tasks (`internal: true`)
- Preserves task order

**Key Function**: `parse_taskfile(filepath: Path, namespace: str, outputter: Outputter) -> list[tuple[str, str, str]]`

**Returns**: List of `(group, task_name, description)` tuples

**Helper Functions**:

- `_extract_task_name(line: str) -> str | None`
- `_extract_description(line: str) -> str | None`
- `_is_internal_task(line: str) -> bool`
- `_save_task_if_valid(...) -> None`

### 5. Output (`output.py`)

Handles output formatting with multiple strategies:

**Protocol**: `Outputter`

- Defines interface for output implementations
- Methods: `output_single()`, `output_all()`, `output_error()`, etc.

**Implementations**:

#### TextOutputter

- Colored terminal output
- Group headers with formatting
- Task list with descriptions
- Respects color settings

#### JsonOutputter

- Structured JSON output
- Task metadata (group, name, full_name, description)
- No color codes
- Machine-readable format

**Color Management**: `Colors` class

- ANSI color codes
- Global enable/disable
- TTY-aware

## Data Flow

### 1. Initialization

```python
# Parse arguments and load config
config = Config(argv)

# Select outputter
outputter = JsonOutputter() if config.args.json_output else TextOutputter()

# Disable colors if needed
if not config.colorize or config.args.json_output:
    Colors.disable()
```

### 2. Discovery

```python
# Find Taskfile
if namespace:
    taskfile = config.discovery.find_namespace_taskfile(namespace)
else:
    taskfile = config.discovery.find_main_taskfile()
```

### 3. Parsing

```python
# Parse tasks
tasks = parse_taskfile(taskfile, namespace, outputter)
# Returns: [(group, task_name, description), ...]
```

### 4. Output

```python
# Display results
outputter.output_single(namespace, tasks)
```

## Design Decisions

### Why Not Full YAML Parser?

- **Performance**: Line-by-line parsing is faster
- **Simplicity**: No external dependencies
- **Sufficient**: Only need task names and descriptions
- **Robust**: Handles malformed YAML gracefully

### Why Protocol-Based Outputters?

- **Extensibility**: Easy to add new output formats
- **Testability**: Mock outputters for testing
- **Separation**: Output logic separate from business logic
- **Type Safety**: Protocol ensures interface compliance

### Why Multiple Search Directories?

- **Flexibility**: Support shared task libraries
- **Monorepos**: Search across multiple projects
- **Reusability**: Common tasks in shared locations
- **Priority**: First match wins (explicit ordering)

### Why Namespace Support?

- **Organization**: Separate concerns (dev, test, deploy)
- **Clarity**: Clear task ownership
- **Scalability**: Large projects with many tasks
- **Modularity**: Independent Taskfile management

## Error Handling

### Graceful Degradation

- Missing Taskfile: Clear error message with tried paths
- Parse errors: Log warning, continue processing
- Invalid namespace: Suggest available namespaces
- No tasks found: Empty output (not an error)

### Exit Codes

- `0`: Success
- `1`: Error (Taskfile not found, invalid namespace, etc.)

## Testing Strategy

### Unit Tests

- Individual function testing
- Mock dependencies
- Edge case coverage
- Fast execution

### End-to-End Tests

- Full CLI invocation
- Subprocess testing
- Real Taskfile parsing
- Integration verification

### Test Organization

```
tests/
├── unit/           # Unit tests
│   ├── test_config.py
│   ├── test_discovery.py
│   ├── test_output.py
│   ├── test_parser.py
│   └── test_taskfile_help.py
└── e2e/            # End-to-end tests
    └── test_cli.py
```

## Performance Characteristics

- **Startup**: < 50ms (no heavy dependencies)
- **Parsing**: O(n) where n = number of lines
- **Memory**: Minimal (streaming line-by-line)
- **Disk I/O**: Single file read per Taskfile

## Future Extensibility

Potential enhancements:

1. **Additional Output Formats**: XML, YAML, Markdown
2. **Caching**: Cache parsed results for large Taskfiles
3. **Validation**: Validate Taskfile structure
4. **Auto-completion**: Shell completion support
5. **Task Dependencies**: Show task dependency graph
