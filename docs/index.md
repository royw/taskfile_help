# Taskfile Help

A dynamic Taskfile help generator that parses Taskfile YAML files and outputs organized, colored help text
similar to `task --list`, but with automatic grouping and namespace support.

## Features

- 🎨 **Colored Output**: Automatic color support with TTY detection
- 📦 **Namespace Support**: Organize tasks across multiple Taskfiles
- 🔍 **Smart Search**: Search multiple directories for Taskfiles
- 📊 **JSON Output**: Export task information in JSON format
- 🎯 **Group Organization**: Automatic task grouping using comment markers
- 🔒 **Internal Tasks**: Hide implementation details with `internal: true`
- ⚡ **Fast**: Simple line-by-line parsing without full YAML overhead

## Quick Start

Install the package:

```bash
pip install taskfile-help
```

Show help for your main Taskfile:

```bash
taskfile-help
```

Show help for a specific namespace:

```bash
taskfile-help dev
```

Show all available tasks across all Taskfiles:

```bash
taskfile-help all
```

## Example Output

![task help](images/task_help.png)

## Why Taskfile Help?

The built-in `task --list` command is useful, but has limitations:

- No automatic grouping of related tasks
- No namespace support for multiple Taskfiles
- Limited customization options

**taskfile-help** solves these problems by providing:

- Automatic task grouping using comment markers
- Support for multiple Taskfiles with namespaces
- Flexible search paths and configuration
- JSON output for integration with other tools
- Consistent color handling (respects TTY detection)

## Creating Help Tasks

```yaml
version: '3'

tasks:
  # === Main Tasks ===
  # ...
  # === Help ===
  help:
    desc: Show available tasks from this main Taskfile
    summary: Displays tasks from this main Taskfile, nicely grouped and formatted
    cmd: taskfile-help main
    silent: true  # Suppress task command echo

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
    silent: true  # Suppress task command echo
```

Now you can run:

```bash
task help           # Main tasks only
task help:all       # All tasks from all namespaces (Main + Dev + ...)
task help:<namespace>   # Tasks from the given namespace
task help:?         # List all namespaces (Dev, Test, ...)
```

The wildcard task (`help:*`) eliminates the need to add help tasks to each namespace Taskfile.

See [Configuration](setup/configuration.md) for more details.

## Next Steps

- [Installation Guide](setup/installation.md) - Detailed installation instructions
- [Quick Start](setup/quickstart.md) - Get up and running quickly
- [Configuration](setup/configuration.md) - Configure taskfile-help for your project
- [API Reference](reference/taskfile_help/index.md) - Complete API documentation
