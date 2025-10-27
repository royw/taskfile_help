# Taskfile Help

A dynamic Taskfile help generator that parses Taskfile YAML files and outputs organized, colored help text similar to `task --list`, but with automatic grouping and namespace support.

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
taskfile-help --all
```

## Example Output

```
=== Build ===
  build         Build the project
  compile       Compile sources

=== Testing ===
  test          Run tests
  test:unit     Run unit tests only
  test:e2e      Run end-to-end tests
```

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

## Next Steps

- [Installation Guide](setup/installation.md) - Detailed installation instructions
- [Quick Start](setup/quickstart.md) - Get up and running quickly
- [Configuration](setup/configuration.md) - Configure taskfile-help for your project
- [API Reference](reference/) - Complete API documentation
