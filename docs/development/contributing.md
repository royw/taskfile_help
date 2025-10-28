# Contributing

Thank you for considering contributing to taskfile-help!

## How to Contribute

### Reporting Bugs

1. Check existing issues
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Suggesting Features

1. Check existing feature requests
2. Create a new issue describing:
   - Use case
   - Proposed solution
   - Alternative approaches

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Run all checks: `task make`
7. Submit pull request

## Development Process

1. **Setup**: Follow the [Development Guide](guide.md)
2. **Code**: Write clean, tested code
3. **Test**: Ensure >90% coverage
4. **Document**: Update relevant docs
5. **Review**: Address feedback

## Code Standards

### General

- **Type hints**: All functions must have type hints
- **Tests**: Unit tests for all new code
- **Formatting**: Use ruff for formatting
- **Linting**: Pass all linters (ruff, mypy, pylint)

### Docstrings

- **Style**: Use Google-style docstrings
- **`__init__.py` files**: Only docstrings in `__init__.py` files (easier to maintain)
- **Module docstrings**: All modules must have a module docstring that explains what is in the module and optionally why the module exists (aids maintainers)

### Code Quality

- **Complexity**: Cyclomatic complexity shall be ≤10
  - Valid reason required for complexities >5
- **No emojis**: Do not use emojis in production code (use words instead to lower chance of misinterpretation)
- **No hard-coded paths**: Do not use hard-coded paths (e.g., use `tempfile` package instead of `/tmp`)

## Commit Messages

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Refactoring
- `chore:` Maintenance

## Questions?

- Open a discussion on GitHub
- Check existing documentation
- Review closed issues
