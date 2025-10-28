# Git Hooks

This directory contains custom git hooks for the project.

## Available Hooks

### commit-msg

Enforces conventional commit message format before allowing the commit.

**Features:**

- Validates commit messages follow conventional commit format
- Provides helpful error messages with examples
- Allows merge and revert commits
- Prevents commits with invalid format

**Supported commit types:**

- `feat:` → New feature (added to CHANGELOG)
- `fix:` → Bug fix (added to CHANGELOG)
- `docs:` → Documentation changes (added to CHANGELOG)
- `refactor:` → Code refactoring (added to CHANGELOG)
- `perf:` → Performance improvements (added to CHANGELOG)
- `test:` → Test-related changes
- `chore:` → Maintenance tasks
- `style:` → Code style/formatting
- `ci:` → CI/CD changes
- `build:` → Build system changes
- `revert:` → Revert previous commits

### post-commit

Automatically updates `CHANGELOG.md` with commit messages following conventional commit format.

**Features:**

- Parses conventional commit messages
- Adds entries to appropriate sections in `[Unreleased]`
- Amends the commit to include CHANGELOG updates
- Avoids infinite loops
- Skips non-conventional commits

**Types added to CHANGELOG:** `feat`, `fix`, `docs`, `refactor`, `perf`

**Types skipped:** `test`, `chore`, `style`, `ci`, `build`, `revert`

## Installation

### Option 1: Using Task (Recommended)

```bash
task git:hooks:install
```

### Option 2: Manual Installation

```bash
# Configure git to use this hooks directory
git config core.hooksPath .githooks

# Make hooks executable
chmod +x .githooks/*
```

### Option 3: Symlink (Alternative)

```bash
# Link individual hooks
ln -sf ../../.githooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## Disabling Hooks

### Temporarily (for one commit)

```bash
git commit --no-verify -m "your message"
```

### Permanently

```bash
# Revert to default hooks directory
git config --unset core.hooksPath

# Or remove symlinks
rm .git/hooks/post-commit
```

## Testing Hooks

Test the post-commit hook:

```bash
# Make a test commit
echo "test" >> test.txt
git add test.txt
git commit -m "feat: add test feature"

# Check if CHANGELOG.md was updated
git log -1 --stat
```

## Troubleshooting

### Hook not running

1. Check if hooks are executable:

   ```bash
   ls -la .githooks/
   ```

2. Verify git configuration:

   ```bash
   git config core.hooksPath
   ```

3. Check for errors:

   ```bash
   # Run hook manually
   .githooks/post-commit
   ```

### CHANGELOG not updating

1. Ensure CHANGELOG.md exists
2. Verify `[Unreleased]` section exists
3. Check that appropriate subsections exist (`### Added`, `### Fixed`, etc.)
4. Use conventional commit format: `type: description`

## Hook Behavior

### commit-msg Hook

Runs **before** the commit is created:

1. ✅ Validates commit message format
2. ✅ Checks against allowed types
3. ✅ Rejects invalid messages with helpful error
4. ✅ Allows merge and revert commits
5. ✅ Prevents commits with bad format

**Example:**

```bash
# Invalid commit - rejected
git commit -m "added new feature"
# ❌ ERROR: Commit message does not follow conventional commit format!

# Valid commit - accepted
git commit -m "feat: add new feature"
# ✅ Commit created
```

### post-commit Hook

Runs **after** the commit is created:

1. ✅ Parses the commit message
2. ✅ Determines the appropriate CHANGELOG section
3. ✅ Adds an entry with commit hash
4. ✅ Amends the commit to include CHANGELOG
5. ✅ Prevents infinite loops
6. ✅ Skips non-conventional commits

**Example:**

```bash
# Commit message
git commit -m "feat: add auto-completion support"

# CHANGELOG.md entry added automatically
### Added
- add auto-completion support (a1b2c3d)
```

## Notes

- The hook uses `--amend` to include CHANGELOG in the same commit
- This means the commit hash in CHANGELOG may differ slightly
- The hook is safe and won't break your commits
- You can always edit CHANGELOG.md manually if needed
