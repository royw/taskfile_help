# End-to-End Tests

This directory contains end-to-end tests for the `taskfile-help` CLI tool.

## Test Coverage

### CLI Help Tests (`TestCLIHelp`)

Tests that verify the help output works correctly through different invocation methods:

- **`test_python_module_help`**: Verifies `python3 -m taskfile_help -h` displays help
- **`test_console_script_help`**: Verifies `.venv/bin/taskfile-help -h` displays help

### CLI Functionality Tests (`TestCLIWithTaskfiles`)

Tests that verify the CLI works correctly with actual Taskfile content:

- **`test_all_with_color_and_search_dirs`**: Tests `--all` flag with color enabled using `--search-dirs`
- **`test_no_color_from_current_dir`**: Tests `--no-color` flag disables colors even when output is a TTY
- **`test_specific_namespace`**: Tests showing a specific namespace (e.g., `test`)
- **`test_piped_output_no_color`**: Tests that piped output (e.g., `dev | cat`) doesn't include ANSI color codes
- **`test_all_flag_shows_all_namespaces`**: Tests `--all` flag displays all namespaces
- **`test_json_output`**: Tests `--json` flag produces valid JSON output
- **`test_verbose_output`**: Tests `--verbose` flag shows search directories
- **`test_search_dirs_with_multiple_paths`**: Tests `--search-dirs` with colon-separated paths
- **`test_nonexistent_namespace`**: Tests error handling for nonexistent namespaces
- **`test_no_taskfile_error`**: Tests error handling when no Taskfile exists

## Test Fixtures

### `taskfiles_dir`

Creates a temporary directory with three sample Taskfiles:

1. **`Taskfile.yaml`** (main): Contains build and test tasks
2. **`Taskfile-dev.yml`** (dev namespace): Contains development tasks
3. **`Taskfile-test.yaml`** (test namespace): Contains testing tasks

Each Taskfile includes:

- Multiple tasks with descriptions
- Group comments (e.g., `# === Build ===`)
- Realistic task structure

## Running Tests

```bash
# Run all e2e tests
uv run pytest tests/e2e/ -v

# Run specific test class
uv run pytest tests/e2e/test_cli.py::TestCLIHelp -v

# Run specific test
uv run pytest tests/e2e/test_cli.py::TestCLIHelp::test_python_module_help -v

# Run with coverage
uv run pytest tests/e2e/ --cov=src/taskfile_help
```

## Key Testing Patterns

1. **Subprocess Testing**: Uses `subprocess.run()` to test actual CLI invocation
2. **Mock TTY**: Uses `patch("sys.stdout.isatty")` to simulate terminal vs piped output
3. **Temporary Directories**: Uses `tmp_path` fixture for isolated test environments
4. **Output Capture**: Uses `capsys` fixture to capture and verify stdout/stderr
5. **Monkeypatch**: Uses `monkeypatch.chdir()` to change working directory for tests
