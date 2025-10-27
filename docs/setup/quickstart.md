# Quick Start

This guide will help you get started with taskfile-help in minutes.

## Basic Usage

### Show Main Taskfile Help

```bash
taskfile-help
# or
taskfile-help main
```

This displays all public tasks from `Taskfile.yml` or `Taskfile.yaml` in the current directory.

### Show Namespace Help

If you have namespace-specific Taskfiles (e.g., `Taskfile-dev.yml`, `Taskfile-test.yml`):

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

```
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

Now you can access each namespace:

```bash
taskfile-help          # Main tasks
taskfile-help dev      # Development tasks
taskfile-help test     # Testing tasks
taskfile-help all      # All tasks from all namespaces
```

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
