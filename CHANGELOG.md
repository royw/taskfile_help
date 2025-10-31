# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed
- update documentation to reflect wildcard help task pattern (ace6be7)

### Fixed

## [0.2.5] - 2025-10-30

### Added

- add release:pypi and release:pypi-test tasks (3ba9b39)

### Changed

- use absolute image URLs for PyPI compatibility (34ceea0)

### Fixed

## [0.2.4] - 2025-10-29

### Added

### Changed

- remove completed features from future plans (17c1d3e)
- add completion documentation to navigation and enable strict mode (b50d574)

### Fixed

## [0.2.3] - 2025-10-29

### Added

### Changed

- add summary fields to all public tasks in Taskfiles (3db875d)
- improve Taskfile.yml vars configuration (5332a1c)
- derive APP_NAME from pyproject.toml (d815a11)

### Fixed

## [0.2.2] - 2025-10-29

### Added

- add shell autocompletion support (f0f898c)

### Changed

### Fixed

## [0.2.1] - 2025-10-28

### Added

- add Taskfile validation with YAML structure checking (606a1fd)

- add help tasks to all namespace Taskfiles (bd11cf3)

- add default tasks to all namespace Taskfiles (8af0407)

### Changed

- add comprehensive validation documentation (0977b87)

- move environment tasks to dedicated Taskfile-env.yml (8f1dbad)

- move release tasks to dedicated Taskfile-release.yml (59ced19)

- move formatting tasks to dedicated Taskfile-format.yml (3401386)

- move testing tasks to dedicated Taskfile-test.yml (21aef11)

- move linting tasks to dedicated Taskfile-lint.yml (ecc2c61)

- add githooks.md to mkdocs navigation (bb1a7a3)

- move metrics tasks to dedicated Taskfile-metrics.yml (7cc1d7d)

- move documentation tasks to dedicated Taskfile-docs.yml (fbe3058)

- remove \_output helper task and use direct echo commands (225c7ee)

### Fixed

- call make task from root namespace in release:build (53b17ab)

- update build task dependency to use env:clean namespace (723f68e)

- remove incorrect cd .. from Taskfile-metrics.yml SRC variable (5c090fb)

- correct VERSION variable scope in release:tag task (7f191e4)

## [0.2.0] - 2025-10-28

### Added

- Git hooks for conventional commits and automated CHANGELOG updates
- Namespace suggestion when invalid namespace is requested
- Support for lowercase main taskfile names (`taskfile.yml`, `taskfile.yaml`)
- Comprehensive edge case testing for namespace discovery

### Changed

- pre-release code cleanup and documentation improvements (7e07d8b)

- reorganize version and release tasks with namespace support (1acb551)

- add git hooks and CHANGELOG workflow to development guide (08dbce9)

- Refactored namespace taskfile discovery to use regex patterns

- Updated all documentation to reflect complete taskfile naming support

- Enhanced error messages to suggest available namespaces

### Fixed

- correct task references to \_bumper in version namespace (84d42e3)

- Infinite loop prevention in post-commit hook

- Documentation accuracy for taskfile naming conventions

## [0.1.0] - 2025-10-27

### Initial Release

- Initial release of taskfile-help
- Dynamic Taskfile help generator with automatic grouping
- Namespace support for organizing tasks across multiple Taskfiles
- Support for main Taskfiles: `Taskfile.yml`, `Taskfile.yaml`, `taskfile.yml`, `taskfile.yaml`
- Support for namespace Taskfiles: `[Tt]askfile[-_]<namespace>\.ya?ml`
- Colored output with automatic TTY detection
- JSON output format (`--json` flag)
- Multiple search directory support (`--search-dirs` flag)
- Verbose mode (`--verbose` flag)
- Special 'all' namespace to show all Taskfiles
- Task visibility rules (public vs internal tasks)
- Automatic task grouping using `# === Group Name ===` markers
- Configuration via `pyproject.toml`
- Comprehensive test suite (145 unit tests + 13 e2e tests)
- Complete documentation:
  - Installation guide
  - Configuration guide
  - Quickstart guide
  - Development guide
  - Architecture documentation
  - Contributing guidelines

### Features

- **Namespace Support**: Organize tasks across multiple Taskfiles

  - Main Taskfile for core tasks
  - Namespace Taskfiles for specialized tasks (dev, test, deploy, etc.)
  - Cross-namespace task visibility

- **Automatic Grouping**: Tasks are automatically grouped using comment markers

  - Preserves order as defined in Taskfile
  - Clear visual separation of task categories

- **Smart Output**:

  - Colored output for terminals
  - Plain text for pipes and redirects
  - JSON format for programmatic use

- **Flexible Discovery**:

  - Search in current directory by default
  - Multiple search directories supported
  - First match wins (priority-based)

- **Task Visibility**:

  - Public tasks: Have `desc` field and no `internal: true`
  - Internal tasks: Marked with `internal: true` (hidden from help)
  - Tasks without descriptions are excluded

### Technical Details

- Python 3.11+ required
- Zero external dependencies (stdlib only)
- Line-by-line parsing (not a full YAML parser)
- Fast startup (< 50ms)
- Minimal memory footprint
- 99% test coverage

### CI/CD

- GitHub Actions workflows for testing and linting
- Automated testing on push and pull requests
- MkDocs documentation deployment
- Status badges in README

[0.1.0]: https://github.com/royw/taskfile-help/releases/tag/v0.1.0
[unreleased]: https://github.com/royw/taskfile-help/compare/v0.1.0...HEAD
