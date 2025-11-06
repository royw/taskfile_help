# Taskfile-Help

A dynamic [Taskfile](https://taskfile.dev/) help generator that parses Taskfile YAML files and outputs organized, colored help text
similar to `task --list`, but with automatic grouping, namespace, and search support.

## Features

- **Group Organization**: Automatic task grouping using comment markers
- **Namespace Support**: Organize tasks across multiple Taskfiles
- **Smart Search**: Search across namespaces, groups, task names, and descriptions with multi-pattern AND logic
- **Multi-Pattern Search**: Filter tasks with multiple patterns and regexes (all must match)
- **JSON Output**: Export task information in JSON format
- **Colored Output**: Automatic color support with TTY detection
- **Internal Tasks**: Hide implementation details with `internal: true`
- **Fast**: Simple line-by-line parsing without full YAML overhead

**What is a Group?**

In lieu of a task tag, a group is a set of tasks organized under a group comment marker. Group comments follow a known pattern like the default
pattern: `# === <group name> ===` and all tasks following the comment belong to that group until the next group comment or end of file.

**Links:**

- [Taskfile.dev](https://taskfile.dev/)
- [Documentation](https://royw.github.io/taskfile_help/)
- [GitHub Repository](https://github.com/royw/taskfile_help)
- [Issue Tracker](https://github.com/royw/taskfile_help/issues)

## Quick Start

Install the package:

```bash
pipx install taskfile-help
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

## Why Taskfile-Help?

The built-in `task --list` command is useful, but has limitations:

- No automatic grouping of related tasks
- No namespace support for multiple Taskfiles
- Limited customization options

**taskfile-help** solves these problems by providing:

- Automatic task grouping using comment markers
- Support for multiple Taskfiles with namespaces
- List by namespace or search across namespaces, groups, task names, and descriptions
- Flexible search paths and configuration
- Configuration in environment, .env, pyproject.toml, or command-line arguments
- JSON output for integration with other tools
- Consistent color handling (respects TTY detection)

### Configuration Matrix

| Option | CLI Flag | Environment Variable(s) | pyproject.toml | .env File | Default |
|--------|----------|------------------------|----------------|-----------|---------|
| **search-dirs** | `--search-dirs`, `-s` | `TASKFILE_HELP_SEARCH_DIRS` | `search-dirs` | ✓ | Current directory |
| **no-color** | `--no-color` | `NO_COLOR`, `TASKFILE_HELP_NO_COLOR` | `no-color` | ✓ | Auto-detect TTY |
| **group-pattern** | `--group-pattern` | `TASKFILE_HELP_GROUP_PATTERN` | `group-pattern` | ✓ | `\s*#\s*===\s*(.+?)\s*===` |
| **verbose** | `--verbose`, `-v` | - | - | - | `false` |
| **json** | `--json` | - | - | - | `false` |

**Priority Order:** Command-line > Environment Variables > pyproject.toml > Defaults

## Creating Help Tasks

```yaml
version: '3'

tasks:
  # === Main Tasks ===
  # ...
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

Now you can run:

```bash
task help           # Main tasks only
task help:all       # All tasks from all namespaces (Main + Dev + ...)
task help:<namespace>   # Tasks from the given namespace
task help -- <namespace> <namespace> ...   # Tasks from the given namespace(s)
task help:"<namespace> <namespace> ..."   # Tasks from the given namespace(s)
task help:?         # List all namespaces (Dev, Test, ...)
```

The wildcard task (`help:*`) eliminates the need to add help tasks to each namespace Taskfile.

## Searching for Tasks

Add a search task wrapper for convenient searching:

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

Now you can search using simple commands:

```bash
task search:python              # Search for "python"
task search -- python           # Search for "python"
task search:"version minor"     # Search for both "version" AND "minor"
task search -- version minor   # Search for "test" AND "minor"
task search -- --regex "m\S+or"     # Search for "minor", "major", "import", "mdformat"
task search -- --regex "m.*or" --regex "b\S+p"   # Search for "minor" or "major" AND "bump"
task search -- --regex "m.*or" bump   # Search for "minor" or "major" AND "bump"
task search:"bump --regex m\S+or"  # Search for "bump" AND "minor" or "major"
taskfile-help search test coverage  # Direct command with multiple patterns
```

Search features:

- Searches across namespace names, group names, task names, AND descriptions
- Multiple patterns use AND logic (all must match)
- Supports multiple `--regex` options for advanced filtering
- Case-insensitive substring matching

## Global Options

Global options can be placed before or after any subcommand:

- `--no-color` - Disable colored output
- `-s, --search-dirs DIRS` - Colon-separated list of directories to search for taskfiles
- `-v, --verbose` - Show verbose output including search directories
- `--json` - Output tasks in JSON format
- `--completion SHELL` - Generate completion script for specified shell
- `--install-completion [SHELL]` - Install completion script
- `-h, --help` - Show help message

Examples:

```bash
# Global options before subcommand
taskfile-help --no-color namespace dev
taskfile-help --json search test

# Global options after subcommand
taskfile-help namespace dev --no-color
taskfile-help search test --json

# Mixed positions
taskfile-help --json namespace dev --verbose
```

See [Configuration](setup/configuration.md) for more details.

## Next Steps

- [Installation Guide](setup/installation.md) - Detailed installation instructions
- [Quick Start](setup/quickstart.md) - Get up and running quickly
- [Configuration](setup/configuration.md) - Configure taskfile-help for your project
- [API Reference](reference/taskfile_help/index.md) - Complete API documentation
