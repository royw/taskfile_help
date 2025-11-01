# Quick Start

This guide will help you get started with taskfile-help in minutes.

## Basic Usage

### Show Main Taskfile Help

```bash
taskfile-help
# or
taskfile-help main
```

This displays all public tasks from your main Taskfile (e.g., `Taskfile.yml`, `Taskfile.yaml`, `taskfile.yml`, or `taskfile.yaml`) in the current directory.

### Show Namespace Help

If you have namespace-specific Taskfiles (e.g., `Taskfile-dev.yml`, `Taskfile_test.yaml`, `taskfile-rag.yml`):

```bash
taskfile-help dev
taskfile-help test
```

### Show All Tasks

Display tasks from all Taskfiles:

```bash
taskfile-help all
```

## Organizing Your Taskfile

### Adding Task Groups

Use comment markers to group related tasks:

```yaml
version: '3'

tasks:
  # === Build ===
  build:
    desc: Build the project
    cmds:
      - go build

  compile:
    desc: Compile sources
    cmds:
      - make compile

  # === Testing ===
  test:
    desc: Run all tests
    cmds:
      - go test ./...

  test:unit:
    desc: Run unit tests only
    cmds:
      - go test ./... -short
```

The output will be automatically grouped:

```text
=== Build ===
  build         Build the project
  compile       Compile sources

=== Testing ===
  test          Run all tests
  test:unit     Run unit tests only
```

### Hiding Internal Tasks

Mark implementation tasks as internal to hide them from help:

```yaml
tasks:
  deploy:
    desc: Deploy the application
    cmds:
      - task: _build
      - task: _push

  _build:
    desc: Internal build step
    internal: true
    cmds:
      - docker build -t myapp .

  _push:
    desc: Internal push step
    internal: true
    cmds:
      - docker push myapp
```

Only `deploy` will appear in the help output.

## Using Namespaces

Create separate Taskfiles for different concerns:

### Main Taskfile (Taskfile.yml)

```yaml
version: '3'

tasks:
  # === Build ===
  build:
    desc: Build the application
    cmds:
      - go build

  # === Help ===
  help:
    desc: Show available tasks from this main Taskfile
    summary: Displays tasks from this main Taskfile, nicely grouped and formatted
    cmd: taskfile-help main
    silent: true

  help:*:
    desc: Show available tasks for the given namespace(s)
    summary: |
      Displays tasks from for the given namespace or all Taskfiles if "all" is specified or list available namespaces if "?" is specified
      help:<namespace>    - Displays tasks from the given namespace
      help:all            - Displays tasks from all Taskfiles
      help:?              - Lists available namespaces
    vars:
      NAMESPACE: '{{index .MATCH 0}}'
    cmd: taskfile-help {{.NAMESPACE}}
    silent: true
```

### Development Taskfile (Taskfile-dev.yml)

```yaml
version: '3'

tasks:
  # === Development ===
  serve:
    desc: Start development server
    cmds:
      - go run main.go

  watch:
    desc: Watch for changes
    cmds:
      - air
```

### Testing Taskfile (Taskfile-test.yml)

```yaml
version: '3'

tasks:
  # === Testing ===
  unit:
    desc: Run unit tests
    cmds:
      - go test ./... -short

  integration:
    desc: Run integration tests
    cmds:
      - go test ./... -run Integration
```

Now you can access each namespace using the wildcard help task:

```bash
task help              # Main tasks only
task help:dev          # Development tasks
task help:test         # Testing tasks
task help:all          # All tasks from all namespaces
task help:?            # List all available namespaces
```

The wildcard task (`help:*`) in the main Taskfile eliminates the need to add help tasks to each namespace Taskfile.

## Searching for Tasks

### Using the Search Command

Search across all taskfiles for tasks matching specific criteria:

```bash
# Search by single pattern
taskfile-help search test
taskfile-help search build

# Search with multiple patterns (AND logic - all must match)
taskfile-help search version bump
taskfile-help search minor version

# Search with regex
taskfile-help search --regex "^test"
taskfile-help search --regex "test" --regex "unit"

# Combine patterns and regexes
taskfile-help search version --regex "bump"
```

### Adding a Search Task Wrapper

For convenience, add a search task to your main Taskfile:

```yaml
  # === Search ===
  search:*:
    desc: Search for tasks
    summary: Search for tasks in all Taskfiles
    vars:
      PATTERN: '{{index .MATCH 0}}'
    cmd: taskfile-help search {{.PATTERN}}
    silent: true
```

Now you can search using the task command:

```bash
task search:python              # Search for "python"
task search:"version minor"     # Search for both "version" AND "minor"
task search:test                # Search for "test"
```

### Search Behavior

- Searches across namespace names, group names, task names, AND descriptions
- Multiple patterns use AND logic (all must match)
- Multiple regexes use AND logic (all must match)
- Case-insensitive substring matching for patterns
- Full regex support for regex filters

## Common Options

### Disable Colors

```bash
taskfile-help --no-color
```

### JSON Output

```bash
taskfile-help --json
```

Output format:

```json
{
  "tasks": [
    {
      "group": "Build",
      "name": "build",
      "full_name": "build",
      "description": "Build the project"
    }
  ]
}
```

### Search in Different Directory

```bash
taskfile-help --search-dirs /path/to/project
taskfile-help -s ../other-project
```

### Verbose Output

```bash
taskfile-help --verbose
```

Shows which directories are being searched.

## Next Steps

- [Configuration](configuration.md) - Learn about advanced configuration options and integration with Taskfiles
- [API Reference](../reference/taskfile_help/index.md) - Explore the complete API documentation
