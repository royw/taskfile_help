# TwoStepParser Module

## Overview

The `TwoStepParser` is a reusable module that implements two-pass argument parsing, allowing global options to be placed before or after subcommands. This provides a more flexible and user-friendly command-line interface.

## Motivation

Standard `argparse` requires global options to appear before subcommands:

```bash
# Standard argparse - ONLY this works
tool --verbose command arg

# These DON'T work with standard argparse
tool command arg --verbose
tool --verbose command --output file arg
```

The `TwoStepParser` enables all these variations by parsing arguments in two passes.

## How It Works

### Two-Pass Approach

**First Pass**: Extract global options from anywhere in argv
```python
global_parser = argparse.ArgumentParser(add_help=False)
# Add only global arguments
global_args, remaining_argv = global_parser.parse_known_args(argv)
```

**Second Pass**: Parse complete command structure
```python
command_parser = argparse.ArgumentParser(...)
# Add global arguments + subcommands
command_args = command_parser.parse_args(argv)
```

The final result merges both passes, using global options from the first pass (which captures them from anywhere) and command-specific options from the second pass.

## Usage

### Basic Example

```python
from taskfile_help.two_step_parser import TwoStepParser

# Create parser
parser = TwoStepParser(description="My CLI tool")

# Add global options
parser.add_global_argument("--verbose", "-v", action="store_true")
parser.add_global_argument("--output", "-o", type=str)

# Add commands
build_cmd = parser.add_command("build", help="Build the project")
build_cmd.add_argument("target", help="Build target")

test_cmd = parser.add_command("test", help="Run tests")
test_cmd.add_argument("--coverage", action="store_true")

# Parse arguments
args = parser.parse_args()
```

### Flexible Command Structures

All of these work:

```bash
# Global options before command
tool --verbose build release
tool --output out.txt test

# Global options after command
tool build release --verbose
tool test --output out.txt

# Mixed positions
tool --verbose build release --output out.txt
tool --output out.txt test --coverage --verbose
```

## API Reference

### TwoStepParser Class

#### `__init__(description=None, formatter_class=..., **kwargs)`

Create a new two-step parser.

**Parameters:**
- `description` (str, optional): Description for the main parser
- `formatter_class` (type, optional): Formatter class for help output
- `**kwargs`: Additional arguments passed to ArgumentParser

#### `add_global_argument(*args, **kwargs)`

Add a global argument that can appear before or after subcommands.

**Parameters:**
- `*args`: Positional arguments for add_argument (e.g., "--verbose", "-v")
- `**kwargs`: Keyword arguments for add_argument (e.g., action="store_true")

#### `add_command(name, help=None, description=None, **kwargs)`

Add a subcommand parser.

**Parameters:**
- `name` (str): Name of the subcommand
- `help` (str, optional): Short help text
- `description` (str, optional): Long description
- `**kwargs`: Additional arguments passed to add_parser

**Returns:**
- `ArgumentParser`: Parser for the subcommand (use to add command-specific arguments)

#### `parse_args(argv=None)`

Parse arguments using two-step approach.

**Parameters:**
- `argv` (list[str], optional): List of arguments to parse (defaults to sys.argv[1:])

**Returns:**
- `argparse.Namespace`: Parsed arguments

## Comparison with Current Implementation

### Current Implementation (in config.py)

The current `Args.parse_args()` method implements two-pass parsing directly:

```python
@staticmethod
def parse_args(argv: list[str]) -> "Args":
    # First pass: parse global options only
    global_parser = argparse.ArgumentParser(add_help=False)
    Args._add_global_arguments(global_parser, Args._list_of_paths)
    global_args, remaining_argv = global_parser.parse_known_args(argv[1:])
    
    # Second pass: parse commands
    command_parser = argparse.ArgumentParser(...)
    Args._add_global_arguments(command_parser, Args._list_of_paths)
    subparsers = command_parser.add_subparsers(...)
    Args._create_namespace_parser(subparsers, Args._list_of_paths)
    Args._create_search_parser(subparsers, Args._list_of_paths)
    command_args = command_parser.parse_args(argv[1:])
    
    # Merge results
    return Args(
        command=command,
        namespace=namespace,
        # ... use global_args for global options
        no_color=global_args.no_color,
        verbose=global_args.verbose,
        # ...
    )
```

### Using TwoStepParser

The same functionality with `TwoStepParser`:

```python
@staticmethod
def parse_args(argv: list[str]) -> "Args":
    parser = TwoStepParser(description="Dynamic Taskfile help generator")
    
    # Add global options
    parser.add_global_argument("--no-color", action="store_true")
    parser.add_global_argument("--verbose", "-v", action="store_true")
    # ... other global options
    
    # Add namespace command
    namespace_cmd = parser.add_command("namespace", help="Show tasks for namespace")
    namespace_cmd.add_argument("namespace", nargs="*", default=[])
    
    # Add search command
    search_cmd = parser.add_command("search", help="Search for tasks")
    search_cmd.add_argument("patterns", nargs="*")
    search_cmd.add_argument("--regex", action="append")
    
    # Parse
    parsed = parser.parse_args(argv)
    
    # Convert to Args dataclass
    return Args(
        command=parsed.command,
        namespace=parsed.namespace,
        patterns=getattr(parsed, "patterns", None),
        regexes=getattr(parsed, "regexes", None),
        no_color=parsed.no_color,
        verbose=parsed.verbose,
        # ...
    )
```

## Benefits of TwoStepParser

1. **Reusability**: Can be used in other projects
2. **Cleaner Code**: Separates parsing logic from application logic
3. **Easier Testing**: Parser logic can be tested independently
4. **Better Abstraction**: Hides implementation details
5. **Maintainability**: Changes to parsing logic are centralized

## Considerations

### When to Refactor

Refactoring to use `TwoStepParser` would be beneficial if:

- You want to extract this pattern for use in other projects
- You want cleaner separation of concerns
- You want more comprehensive testing of the parsing logic

### When to Keep Current Implementation

The current implementation is fine if:

- The pattern is only used in this project
- The current code is working well and well-tested
- Refactoring would provide minimal benefit

## Testing

The `TwoStepParser` has comprehensive tests in `tests/unit/test_two_step_parser.py`:

- Global options before/after/mixed positions
- Multiple commands
- Command-specific arguments
- Optional and required arguments
- Short and long option forms
- Default values
- Argument choices

Run tests:
```bash
pytest tests/unit/test_two_step_parser.py -v
```

## Example

See `examples/two_step_parser_example.py` for a complete working example.

## Future Enhancements

Potential improvements to `TwoStepParser`:

1. **Mutually Exclusive Groups**: Support for mutually exclusive global options
2. **Argument Groups**: Support for organizing arguments into groups
3. **Custom Actions**: Support for custom argparse actions
4. **Subcommand Aliases**: Support for command aliases
5. **Better Error Messages**: Enhanced error reporting for parsing failures
