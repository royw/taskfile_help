# Shell Auto-completion

`taskfile-help` supports shell auto-completion for namespaces, task names, and command-line flags across multiple shell environments.

## Supported Shells

- **Bash** (4.0+)
- **Zsh** (5.0+)
- **Fish** (3.0+)
- **Tcsh/Csh**
- **Ksh**

## Quick Installation

The easiest way to install completions is using the `--install-completion` command:

```bash
# Auto-detect shell and install
taskfile-help --install-completion

# Or specify shell explicitly
taskfile-help --install-completion bash
taskfile-help --install-completion zsh
taskfile-help --install-completion fish
```

This will:

1. Generate the appropriate completion script for your shell
2. Install it to the standard location
3. Provide instructions for enabling it

## Manual Installation

If you prefer to install completions manually, you can generate the script and place it yourself.

### Bash

```bash
# Generate completion script
taskfile-help --completion bash > ~/.bash_completion.d/taskfile-help

# Add to ~/.bashrc if not already sourced
echo 'source ~/.bash_completion.d/taskfile-help' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

### Zsh

```bash
# Create completion directory
mkdir -p ~/.zsh/completion

# Generate completion script
taskfile-help --completion zsh > ~/.zsh/completion/_taskfile-help

# Add to ~/.zshrc if not already configured
echo 'fpath=(~/.zsh/completion $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

### Fish

```bash
# Create completion directory
mkdir -p ~/.config/fish/completions

# Generate completion script
taskfile-help --completion fish > ~/.config/fish/completions/taskfile-help.fish

# Fish automatically loads completions from this directory
# Reload shell
source ~/.config/fish/config.fish
```

### Tcsh/Csh

```bash
# Create completion directory
mkdir -p ~/.tcshrc.d

# Generate completion script
taskfile-help --completion tcsh > ~/.tcshrc.d/taskfile-help.tcsh

# Add to ~/.tcshrc
echo 'source ~/.tcshrc.d/taskfile-help.tcsh' >> ~/.tcshrc

# Reload shell
source ~/.tcshrc
```

### Ksh

```bash
# Create completion directory
mkdir -p ~/.kshrc.d

# Generate completion script
taskfile-help --completion ksh > ~/.kshrc.d/taskfile-help.ksh

# Add to ~/.kshrc
echo '. ~/.kshrc.d/taskfile-help.ksh' >> ~/.kshrc

# Reload shell
. ~/.kshrc
```

## What Gets Completed

### Namespaces

Tab completion works for namespace names:

```bash
$ taskfile-help <TAB>
all  dev  docs  main  test  release

$ taskfile-help te<TAB>
test
```

### Task Names

Complete task names within a namespace using the colon separator:

```bash
$ taskfile-help test:<TAB>
test:all  test:unit  test:e2e  test:coverage

$ taskfile-help test:u<TAB>
test:unit
```

### Command-line Flags

Complete command-line options:

```bash
$ taskfile-help --<TAB>
--completion  --help  --install-completion  --json  --no-color  --search-dirs  --verbose

$ taskfile-help --no<TAB>
--no-color
```

## How It Works

The completion system uses two mechanisms:

1. **Static completions**: Command-line flags are pre-defined in the completion script
2. **Dynamic completions**: Namespaces and task names are discovered at completion time by calling `taskfile-help --complete <word>`

This means completions automatically update when you add or remove Taskfiles in your project.

## Performance

Completions are designed to be fast:

- Namespace discovery is cached by your shell
- Task name completion only parses the relevant Taskfile
- Completion queries typically complete in under 50ms

## Troubleshooting

### Completions Not Working

1. **Verify installation**:

   ```bash
   # Check if completion script exists
   ls ~/.bash_completion.d/taskfile-help  # for bash
   ls ~/.zsh/completion/_taskfile-help    # for zsh
   ls ~/.config/fish/completions/taskfile-help.fish  # for fish
   ```

2. **Verify sourcing**:

   ```bash
   # Check if completion script is sourced in your RC file
   grep taskfile-help ~/.bashrc  # for bash
   grep taskfile-help ~/.zshrc   # for zsh
   ```

3. **Reload shell**:

   ```bash
   exec $SHELL  # Start a new shell session
   ```

4. **Check for errors**:

   ```bash
   # Test completion manually
   taskfile-help --complete ""
   taskfile-help --complete "test:"
   ```

### Completions Are Outdated

If completions don't reflect recent changes to your Taskfiles:

1. **For most shells**: Completions are generated dynamically, so they should update automatically
2. **For cached completions**: Clear your shell's completion cache:

   ```bash
   # Zsh
   rm ~/.zcompdump*
   compinit
   
   # Bash
   complete -r taskfile-help
   source ~/.bash_completion.d/taskfile-help
   ```

### Permission Errors

If you get permission errors during installation:

```bash
# Ensure directories exist and are writable
mkdir -p ~/.bash_completion.d
chmod 755 ~/.bash_completion.d
```

## Advanced Usage

### Custom Installation Paths

You can generate the completion script and place it anywhere:

```bash
# Generate script
taskfile-help --completion bash > /path/to/custom/location

# Source it in your RC file
echo 'source /path/to/custom/location' >> ~/.bashrc
```

### Multiple Projects

Completions work per-directory based on the Taskfiles in your current working directory. When you `cd` to a different project, completions automatically reflect that project's Taskfiles.

### Search Directories

If you use `--search-dirs` to look for Taskfiles in custom locations, completions will respect that setting:

```bash
# Completions will search in ~/projects/taskfiles
taskfile-help --search-dirs ~/projects/taskfiles <TAB>
```

However, this requires passing the flag each time. For persistent configuration, use `pyproject.toml`:

```toml
[tool.taskfile-help]
search-dirs = ["~/projects/taskfiles"]
```

## Examples

### Basic Namespace Completion

```bash
$ taskfile-help <TAB>
all  dev  docs  main  test

$ taskfile-help d<TAB>
dev  docs
```

### Task Name Completion

```bash
$ taskfile-help test:<TAB>
test:all        test:coverage   test:e2e       test:unit
test:functional test:integration test:sequential

$ taskfile-help test:cov<TAB>
test:coverage
```

### Flag Completion

```bash
$ taskfile-help --<TAB>
--completion           --install-completion  --no-color
--help                 --json                --search-dirs
--verbose

$ taskfile-help -<TAB>
-h  -s  -v
```

## See Also

- [Configuration](configuration.md) - Configure search directories
- [Quick Start](quickstart.md) - Learn how to use taskfile-help
- [Development](../development/contributing.md) - Contribute to the project
