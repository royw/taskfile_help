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
    desc: Show available tasks from a namespace (defaults to main)
    summary: Displays tasks from the given namespace (defaults to main)
    cmd: taskfile-help namespace {{.CLI_ARGS}}
    silent: true  # Suppress task command echo

  help:*:
    desc: Show available tasks for "all" or the given namespace or for "?" list available namespaces
    summary: |
      Displays tasks for "all" or the given namespace or list available namespaces if "?" is specified
      help:<namespace>    - Displays tasks from the given namespace
      help:all            - Displays tasks from all Taskfiles
      help:?              - Lists available namespaces
    vars:
      NAMESPACE: '{{index .MATCH 0}}'
    cmd: taskfile-help namespace {{.NAMESPACE}}
    silent: true  # Suppress task command echo
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
task help -- dev test  # Development and testing tasks
task help:"dev test"   # Development and testing tasks
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
  search:
    desc: Search for tasks
    summary: Search for tasks in all Taskfiles
    cmd: taskfile-help search {{.CLI_ARGS}}
    silent: true  # Suppress task command echo
    
  search:*:
    desc: Search for tasks
    summary: Search for tasks in all Taskfiles
    vars:
      PATTERN: '{{index .MATCH 0}}'
    cmd: taskfile-help search {{.PATTERN}}
    silent: true  # Suppress task command echo
```

Now you can search using the task command:

```bash
task search:python              # Search for "python"
task search -- python           # Search for "python"
task search:"version minor"     # Search for both "version" AND "minor"
task search -- version minor   # Search for "version" AND "minor"
task search -- --regex "m\S+or"     # Search for "minor", "major", "import", "mdformat"
task search -- --regex "m.*or" --regex "b\S+p"   # Search for "minor" or "major" AND "bump"
task search -- --regex "m.*or" bump   # Search for "minor" or "major" AND "bump"
task search:"bump --regex m\S+or"  # Search for "bump" AND "minor" or "major"
```

### Search Behavior

- Searches across namespace names, group names, task names, AND descriptions
- Multiple patterns use AND logic (all must match)
- Multiple regexes use AND logic (all must match)
- Case-insensitive substring matching for patterns
- Full regex support for regex filters

## Global Options

Global options can be placed before or after any subcommand, giving you flexibility in how you structure your commands.

### Available Options

- `--no-color` - Disable colored output
- `-s, --search-dirs DIRS` - Colon-separated list of directories to search for taskfiles
- `-v, --verbose` - Show verbose output including search directories
- `--json` - Output tasks in JSON format
- `--completion SHELL` - Generate completion script for specified shell
- `--install-completion [SHELL]` - Install completion script
- `-h, --help` - Show help message

### Flexible Positioning

```bash
# Global options before subcommand
taskfile-help --no-color namespace dev
taskfile-help --json search test
taskfile-help -v --search-dirs /path namespace all

# Global options after subcommand
taskfile-help namespace dev --no-color
taskfile-help search test --json
taskfile-help namespace all -v --search-dirs /path

# Mixed positions (before and after)
taskfile-help --json namespace dev --verbose
taskfile-help -s /path search test --no-color
```

### Common Usage Examples

#### Disable Colors

```bash
taskfile-help --no-color namespace
taskfile-help namespace --no-color
```

#### JSON Output

```bash
taskfile-help --json namespace
taskfile-help namespace --json
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

#### Search in Different Directory

```bash
taskfile-help --search-dirs /path/to/project namespace
taskfile-help -s ../other-project namespace
taskfile-help namespace -s /path/to/project
```

#### Verbose Output

```bash
taskfile-help --verbose namespace
taskfile-help namespace --verbose
```

Shows which directories are being searched.

## Next Steps

- [Configuration](configuration.md) - Learn about advanced configuration options and integration with Taskfiles
- [API Reference](../reference/taskfile_help/index.md) - Explore the complete API documentation
