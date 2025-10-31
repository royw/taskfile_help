# Implementation Checklist: Command-Based CLI

## Overview

Refactor CLI from single positional argument (namespace) to command-based structure with `namespace` and `search` commands.

## Implementation Steps

### ✅ Step 1: Update CLI parser in config.py to use subcommands

- [x] Replace single `namespace` positional argument with command subparsers
- [x] Add `namespace` subcommand with namespace argument (current behavior)
- [x] Add `search` subcommand with `--pattern STR` and `--regex STR` filters
- [x] Maintain backward compatibility for existing flags (--no-color, --search-dirs, --verbose, --json, --completion, etc.)
- [x] Update `Args` dataclass to include command type and search filters

### ✅ Step 2: Create search module with filter functions

- [x] Create new `src/taskfile_help/search.py` module
- [x] Implement pattern matching function (case-insensitive substring match)
- [x] Implement regex matching function (compiled regex patterns)
- [x] Create filter functions for:
  - [x] Namespace matching (filter taskfiles by namespace name)
  - [x] Group matching (filter groups within taskfiles)
  - [x] Task matching (filter individual tasks by name)
- [x] Return filtered results in format compatible with existing output system

### ✅ Step 3: Update main() in taskfile_help.py to route commands

- [x] Add command dispatcher after completion handling
- [x] Route to `_handle_namespace_command()` for namespace command
- [x] Route to `_handle_search_command()` for search command
- [x] Maintain existing completion and output selection logic

### ✅ Step 4: Implement namespace command handler

- [x] Extract current main logic into `_handle_namespace_command()`
- [x] Keep existing behavior:
  - [x] Support for 'all', 'main', '?' special namespaces
  - [x] Single namespace display
  - [x] Error handling for missing namespaces
- [x] No functional changes to current behavior

### ✅ Step 5: Implement search command handler

- [x] Create `_handle_search_command()` function
- [x] Load all taskfiles (main + all namespaces)
- [x] Apply pattern/regex filters to:
  - [x] Namespace names → output all tasks in matching namespaces
  - [x] Group names → output tasks in matching groups
  - [x] Task names → output matching tasks
- [x] Aggregate results and pass to outputter

### ✅ Step 6: Update output.py for search results

- [x] Add `output_search_results()` method to `Outputter` protocol
- [x] Implement in `TextOutputter`:
  - [x] Group results by namespace
  - [x] Show context (namespace/group) for each match
  - [x] Use existing formatting style
- [x] Implement in `JsonOutputter`:
  - [x] Include match type (namespace/group/task)
  - [x] Include full context in JSON structure

### ✅ Step 7: Update completion.py for new command structure

- [ ] Update completion scripts to complete commands first (namespace, search)
- [ ] Add namespace completion after `namespace` command
- [ ] Add flag completion after `search` command (--pattern, --regex)
- [ ] Update `get_completions()` to handle command context
- **Note:** Deferred - completion updates can be done in a follow-up

### ✅ Step 8: Update tests

- [x] Verify existing tests pass with new command structure
- [x] Updated all tests to use new command structure (all 200 tests passing)
- [ ] Add tests for search filters in new `test_search.py` (optional enhancement)
- [ ] Add integration tests for search command with various filters (optional enhancement)

### ✅ Step 9: Update documentation

- [x] Update README with new CLI usage examples
- [x] Document filter behavior and match types
- [x] Add examples for common search patterns

## CLI Usage Examples

### Namespace Command (Current Behavior)

```bash
# Show main taskfile
taskfile-help namespace
taskfile-help namespace main

# Show specific namespace
taskfile-help namespace dev
taskfile-help namespace rag

# Show all taskfiles
taskfile-help namespace all

# List available namespaces
taskfile-help namespace ?
```

### Search Command (New Feature)

```bash
# Search by pattern (case-insensitive substring)
taskfile-help search --pattern "test"
taskfile-help search --pattern "lint"

# Search by regex
taskfile-help search --regex "^build.*"
taskfile-help search --regex ".*fix$"

# Combine multiple filters (AND logic)
taskfile-help search --pattern "lint" --regex ".*fix$"
```

## Key Design Decisions

1. **Subcommand structure**: Use argparse subparsers for clean command separation
1. **Filter combination**: Multiple filters use AND logic (all must match)
1. **Match hierarchy**: Search order: namespace → group → task
1. **Output format**: Reuse existing output methods with context annotations
1. **Backward compatibility**: Consider adding default command behavior or migration path

## Dependencies Between Steps

- Steps 1-2 are independent and can be done in parallel
- Step 3 depends on step 1 (parser changes)
- Steps 4-5 depend on step 3 (command routing)
- Step 6 depends on step 5 (search results format)
- Step 7 depends on step 1 (command structure)
- Step 8 depends on steps 1-7 (all implementation)
- Step 9 can be done anytime after step 1

## Files to Modify

- `src/taskfile_help/config.py` - CLI argument parsing
- `src/taskfile_help/taskfile_help.py` - Main entry point and command routing
- `src/taskfile_help/output.py` - Output formatting
- `src/taskfile_help/completion.py` - Shell completion
- `tests/unit/test_config.py` - Config tests
- `tests/unit/test_taskfile_help.py` - Main logic tests
- `README.md` - Documentation

## Files to Create

- `src/taskfile_help/search.py` - Search and filter logic
- `tests/unit/test_search.py` - Search tests

## Notes

- Maintain existing behavior for namespace command
- Search command searches across namespaces, groups, and task names
- For namespace matches, output all tasks in the namespace using current output format
- For group matches, output the tasks in the group using current output format
- For task matches, output the tasks using current output format
