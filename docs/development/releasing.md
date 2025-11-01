# Release Process

This document describes the automated release process for taskfile-help.

## Overview

The release process is highly automated using GitHub Actions. When you push a version tag, GitHub Actions automatically:

1. Builds the package
2. Runs the full test suite
3. Creates a GitHub release with built assets
4. Publishes the package to PyPI

## Release Workflow

### 1. Prepare the Release

First, bump the version and prepare the release:

```bash
# Bump version (patch, minor, or major)
task version:bump minor

# Prepare release (runs tests, updates CHANGELOG, commits changes)
task release:build
```

The `release:build` task will:

- Verify working directory is clean
- Check version has been bumped
- Validate CHANGELOG has unreleased changes
- Run full test suite
- Update CHANGELOG with version and date
- Commit release preparation
- Build distribution packages
- Show next steps

### 2. Create and Push the Tag

```bash
task release:tag
```

This creates a git tag for the current version and pushes it to GitHub, which triggers the automated release workflow.

### 3. Monitor the Automated Release

After pushing the tag, GitHub Actions automatically:

1. **Builds the package** - Creates wheel and source distribution
2. **Runs tests** - Ensures everything passes
3. **Creates GitHub Release** - With release notes from CHANGELOG
4. **Uploads assets** - Attaches built packages to the release
5. **Publishes to PyPI** - Makes the package available via `pip install`

Monitor progress at: [GitHub Actions](https://github.com/royw/taskfile_help/actions)

## GitHub Actions Workflows

### Release Workflow (`.github/workflows/release.yml`)

Triggers on: Tag push (`v*`)

Steps:

- Checkout code with full history
- Set up Python 3.13
- Install dependencies with uv
- Run test suite
- Build package
- Extract version from tag
- Extract release notes from CHANGELOG
- Create GitHub release with assets
- Trigger PyPI publish workflow

### Publish Workflow (`.github/workflows/publish.yml`)

Triggers on: GitHub release published

Steps:

- Build distribution packages
- Publish to PyPI using trusted publishing

## Manual Steps (If Needed)

### Manual PyPI Upload

If automatic PyPI publishing fails, you can manually upload:

```bash
# Upload to Test PyPI first
task release:pypi-test

# Then upload to production PyPI
task release:pypi
```

### Manual GitHub Release

If you need to create a release manually:

1. Go to [GitHub Releases](https://github.com/royw/taskfile_help/releases)
2. Click "Draft a new release"
3. Choose the tag
4. Copy release notes from CHANGELOG.md
5. Upload files from `dist/` directory
6. Publish release

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backwards compatible)
- **PATCH** version for bug fixes (backwards compatible)

Use the version bump tasks:

```bash
task version:bump patch   # 0.3.0 -> 0.3.1
task version:bump minor   # 0.3.0 -> 0.4.0
task version:bump major   # 0.3.0 -> 1.0.0
```

## CHANGELOG Management

The CHANGELOG follows [Keep a Changelog](https://keepachangelog.com/) format.

### During Development

Changes are automatically added to the `[Unreleased]` section by the post-commit hook based on conventional commit types:

- `feat:` → Added section
- `fix:` → Fixed section
- `docs:` → Changed section
- `refactor:` → Changed section
- `perf:` → Changed section

### During Release

The `release:build` task automatically:

1. Moves `[Unreleased]` content to a new version section
2. Adds the version number and date
3. Creates a new empty `[Unreleased]` section for future changes

## Troubleshooting

### Release Build Fails

If `task release:build` fails:

- **Uncommitted changes**: Commit or stash changes first
- **Version not bumped**: Run `task version:bump`
- **Empty CHANGELOG**: Make commits with conventional commit types
- **Tests failing**: Fix tests before releasing

### GitHub Actions Fails

If the GitHub Actions workflow fails:

1. Check the [Actions tab](https://github.com/royw/taskfile_help/actions)
2. Review the failed step logs
3. Fix the issue locally
4. Delete the tag: `git tag -d v0.3.1 && git push origin :refs/tags/v0.3.1`
5. Re-run the release process

### PyPI Publishing Fails

If PyPI publishing fails:

1. Check PyPI trusted publishing is configured
2. Verify the package version doesn't already exist on PyPI
3. Use manual upload: `task release:pypi`

## Security

### PyPI Trusted Publishing

This project uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) for secure, token-free publishing:

- No API tokens stored in GitHub secrets
- GitHub Actions authenticates directly with PyPI
- Configured in PyPI project settings

### GitHub Permissions

The release workflow requires:

- `contents: write` - To create releases and upload assets
- `id-token: write` - For PyPI trusted publishing

## Best Practices

1. **Always run tests** before releasing (`task make`)
2. **Review CHANGELOG** before releasing
3. **Use semantic versioning** appropriately
4. **Monitor GitHub Actions** after pushing tags
5. **Test in staging** when possible (Test PyPI)
6. **Keep CHANGELOG updated** with meaningful commit messages

## Quick Reference

```bash
# Complete release process
task version:bump minor    # Bump version
task release:build         # Prepare release
task release:tag           # Create tag (triggers automation)

# Monitor
# Visit: https://github.com/royw/taskfile_help/actions

# Manual fallback (if needed)
task release:pypi-test     # Test PyPI upload
task release:pypi          # Production PyPI upload
```
