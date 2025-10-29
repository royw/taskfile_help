# Configuration

taskfile-help can be configured via command-line arguments or `pyproject.toml`.

## Command-Line Options

### Namespace Selection

```bash
# Show main Taskfile ([Tt]askfile\.ya?ml)
taskfile-help
taskfile-help main

# Show specific namespace ([Tt]askfile[-_](?P<namespace>\w+)\.ya?ml)
taskfile-help dev
taskfile-help test
taskfile-help rag
```

### Show All Taskfiles

```bash
taskfile-help all
```

Displays tasks from all Taskfiles (main + all namespaces).

### Color Control

```bash
# Disable colors
taskfile-help --no-color

# Colors are automatically disabled when:
# - Output is piped (e.g., taskfile-help | cat)
# - Output is redirected (e.g., taskfile-help > file.txt)
# - Using --json output
```

### Search Directories

```bash
# Search in specific directory
taskfile-help --search-dirs /path/to/project
taskfile-help -s /path/to/project

# Search multiple directories (first match wins)
taskfile-help --search-dirs /path1:/path2:/path3
taskfile-help -s ~/projects/main:~/projects/shared

# Relative paths (resolved from current directory)
taskfile-help --search-dirs ../other-project
taskfile-help -s ./subdir:../shared
```

### JSON Output

```bash
taskfile-help --json
taskfile-help dev --json
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
    },
    {
      "group": "Build",
      "name": "compile",
      "full_name": "compile",
      "description": "Compile sources"
    }
  ]
}
```

For namespaces:

```json
{
  "tasks": [
    {
      "group": "Development",
      "name": "serve",
      "full_name": "dev:serve",
      "description": "Start development server"
    }
  ]
}
```

### Verbose Output

```bash
taskfile-help --verbose
taskfile-help -v
```

Shows search directories being used:

```text
Searching in directories:
  /home/user/project
  /home/user/shared
```

## Configuration File (pyproject.toml)

You can configure default settings in `pyproject.toml`:

```toml
[tool.taskfile-help]
search-dirs = [".", "../shared", "~/common"]
```

### Configuration Options

#### search-dirs

List of directories to search for Taskfiles.

```toml
[tool.taskfile-help]
# Single directory
search-dirs = ["."]

# Multiple directories
search-dirs = [".", "../shared", "~/common"]

# Absolute and relative paths
search-dirs = [
    ".",
    "../other-project",
    "/opt/shared-tasks",
    "~/my-tasks"
]
```

**Note**: Command-line arguments take precedence over `pyproject.toml` settings.

## File Naming Conventions

### Main Taskfile

The main Taskfile can be named (case-sensitive, matches regex `[Tt]askfile\.ya?ml`):

- `Taskfile.yml`
- `Taskfile.yaml`
- `taskfile.yml`
- `taskfile.yaml`

**Note**: Uppercase variants (`Taskfile.*`) are preferred and checked first.

### Namespace Taskfiles

Namespace Taskfiles follow the pattern (case-sensitive, matches regex `[Tt]askfile[-_](?P<namespace>\w+)\.ya?ml`):

- `Taskfile-<namespace>.yml`
- `Taskfile-<namespace>.yaml`
- `Taskfile_<namespace>.yml`
- `Taskfile_<namespace>.yaml`
- `taskfile-<namespace>.yml`
- `taskfile-<namespace>.yaml`
- `taskfile_<namespace>.yml`
- `taskfile_<namespace>.yaml`

**Note**: Uppercase variants (`Taskfile*`) and hyphen separator (`-`) are preferred.

Examples:

- `Taskfile-dev.yml` → namespace: `dev`
- `Taskfile_test.yaml` → namespace: `test`
- `taskfile-rag.yml` → namespace: `rag`
- `Taskfile_agent.yml` → namespace: `agent`

## Task Visibility Rules

### Public Tasks

Tasks are public (shown in help) when they have:

1. A `desc` field
2. No `internal: true` flag

```yaml
tasks:
  build:
    desc: Build the project  # Public - has desc
    cmds:
      - go build
```

### Internal Tasks

Tasks are internal (hidden from help) when:

1. Marked with `internal: true`
2. Missing a `desc` field

```yaml
tasks:
  _internal:
    desc: Internal helper
    internal: true  # Hidden - marked internal
    cmds:
      - echo "internal"

  no-desc:
    # Hidden - no desc field
    cmds:
      - echo "no description"
```

## Validation

taskfile-help automatically validates Taskfiles to ensure they conform to Task version 3 specification.

### What is Validated

Validation checks the following:

1. **Version field**
   - Must exist
   - Must equal `'3'` (string, not number or other version)

2. **Tasks section**
   - Must exist
   - Must be a dictionary

3. **Task structure**
   - Each task must be a dictionary
   - Field type validation:
     - `desc`: must be a string
     - `internal`: must be a boolean (`true` or `false`)
     - `cmds`: must be a list or string
     - `deps`: must be a list

### Validation Behavior

- **Always enabled**: Validation runs automatically on every parse
- **Non-fatal**: Warnings are displayed but processing continues
- **Clear messages**: Explains what's wrong and where
- **Fast**: Minimal performance impact (~1-2ms per file)

### Example Warnings

```bash
$ taskfile-help
Warning: Invalid version '2', expected '3'
Warning: Task 'build': 'desc' must be a string, got int
Warning: Task 'test': 'internal' must be a boolean, got str

# Tasks are still shown despite warnings
MAIN Task Commands:

Build:
  task build            - 123
```

### Common Issues

#### Wrong Version

```yaml
# Wrong - number instead of string
version: 3

# Wrong - version 2
version: '2'

# Correct
version: '3'
```

#### Invalid Task Fields

```yaml
tasks:
  build:
    # Wrong - desc must be a string
    desc: 123
    
    # Wrong - internal must be boolean
    internal: "yes"
    
    # Wrong - deps must be a list
    deps: "clean"

  # Correct
  test:
    desc: Run tests
    internal: true
    deps:
      - build
    cmds:
      - pytest
```

### Stderr Output

All validation warnings are written to stderr, so they won't interfere with:

- JSON output (`--json`)
- Piped commands (`taskfile-help | grep ...`)
- Redirected output (`taskfile-help > file.txt`)

## Environment Variables

taskfile-help respects standard terminal behavior:

- **TTY Detection**: Automatically detects if output is to a terminal
- **Color Support**: Colors enabled only when outputting to a TTY
- **Pipe Detection**: Colors disabled when output is piped or redirected

## Search Path Resolution

When searching for Taskfiles:

1. **Absolute paths**: Used as-is

   ```bash
   taskfile-help -s /opt/tasks
   ```

2. **Relative paths**: Resolved from current working directory

   ```bash
   taskfile-help -s ../other-project
   ```

3. **Home directory**: Tilde expansion supported

   ```bash
   taskfile-help -s ~/my-tasks
   ```

4. **Multiple paths**: First match wins

   ```bash
   taskfile-help -s ./local:../shared:/opt/global
   ```

## Priority Order

Configuration is applied in this order (later overrides earlier):

1. Default values (current directory)
2. `pyproject.toml` settings
3. Command-line arguments

Example:

```toml
# pyproject.toml
[tool.taskfile-help]
search-dirs = [".", "../shared"]
```

```bash
# This overrides pyproject.toml
taskfile-help --search-dirs /custom/path
```

## Examples

### Project with Shared Tasks

```toml
# pyproject.toml
[tool.taskfile-help]
search-dirs = [".", "../shared-tasks"]
```

```bash
# Uses both current dir and shared-tasks
taskfile-help

# Override to use only current dir
taskfile-help --search-dirs .
```

### Multi-Repository Setup

```bash
# Search across multiple repos
taskfile-help --search-dirs ~/repos/main:~/repos/shared:~/repos/tools
```

### CI/CD Integration

```bash
# Disable colors for CI logs
taskfile-help --no-color

# Export task list as JSON
taskfile-help --json > tasks.json

# Validate Taskfile has tasks
taskfile-help --json | jq '.tasks | length'
```
