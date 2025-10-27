# taskfile_help

Dynamic Taskfile help generator.

Parses Taskfile YAML files and outputs organized, colored help text similar to
`task --list`, but with automatic grouping and namespace support.

## Usage

```bash
# Show help for main Taskfile.yml in current directory
taskfile_help.py
taskfile_help.py main

# Show help for a specific namespace
taskfile_help.py <namespace>
taskfile_help.py rag
taskfile_help.py dev

# Show help for all Taskfiles
taskfile_help.py --all

# Disable colored output
taskfile_help.py --no-color
taskfile_help.py rag --no-color

# Search in a specific directory (absolute path)
taskfile_help.py --search-dirs /path/to/project
taskfile_help.py rag -s /path/to/project

# Search in a specific directory (relative path)
taskfile_help.py --search-dirs ../other-project
taskfile_help.py -s ./subdir

# Search multiple directories for taskfiles
taskfile_help.py --search-dirs /path1:/path2:/path3
taskfile_help.py -s ~/projects/main:~/projects/shared
taskfile_help.py --search-dirs ../project1:./local:~/shared

# Show verbose output (search directories)
taskfile_help.py --verbose
taskfile_help.py -v rag

# Output in JSON format
taskfile_help.py --json
taskfile_help.py rag --json
```

## Options

- `namespace` - Optional namespace to show help for (e.g., 'rag', 'dev', 'main')
- `--all` - Show help for all taskfiles
- `--no-color` - Disable colored output
- `-s, --search-dirs DIRS` - Colon-separated list of directories to search for taskfiles. Paths may be absolute or relative to current working directory. (default: current working directory)
- `-v, --verbose` - Show verbose output including search directories
- `--json` - Output tasks in JSON format
- `-h, --help` - Show this help message and exit

## Configuration

Settings can be configured in pyproject.toml under \[tool.taskfile-help\]:

```toml
[tool.taskfile-help]
search-dirs = [".", "../shared"]  # List of directories to search
```

Command-line arguments take precedence over pyproject.toml settings.

## File Naming Conventions

- **Main Taskfile**: Taskfile.yml or Taskfile.yaml
- **Namespace Taskfiles**: Taskfile-<namespace>.yml or Taskfile-<namespace>.yaml
  - Examples: Taskfile-rag.yml, Taskfile-dev.yml, Taskfile-agent.yml

## Search Behavior

- By default, searches for taskfiles in the current working directory
- Use --search-dirs (or -s) to search in one or more directories (first match wins)
- Paths can be absolute (/path/to/dir) or relative (../dir, ./subdir)
- Relative paths are resolved from the current working directory
- Taskfiles can be located anywhere in the search path(s)

## Task Organization

Tasks are automatically grouped using comment markers in the Taskfile:

```yaml
# === Group Name ===
task-name:
  desc: Task description
  cmds: [...]

task2-name:
  desc: Task2 description
  cmds: [...]

# === Group2 Name ===
```

Example groups: "Service Management", "Testing", "Build and Release"

The output preserves the order of groups and tasks as they appear in the file.

## Task Visibility

- **Public tasks**: Have a 'desc' field and no 'internal: true' flag
- **Internal tasks**: Marked with 'internal: true' (excluded from help)
- Tasks without descriptions are excluded from help output

## Output Behavior

- **Colors enabled**: When output is to a terminal (TTY) and --no-color is not specified
- **Colors disabled**: When output is piped, redirected, captured, or --no-color is used
- Matches the behavior of 'task --list'

## Integration

Designed to be called from Taskfile help tasks:

```yaml
# In main Taskfile.yml
help:
  desc: Show task help
  cmd: scripts/taskfile_help.py
  silent: true

help:all:
  desc: Show help for all tasks
  cmd: scripts/taskfile_help.py --all
  silent: true

# In namespace Taskfile-rag.yml
help:
  desc: Show RAG task help
  cmd: scripts/taskfile_help.py rag
  silent: true
```
