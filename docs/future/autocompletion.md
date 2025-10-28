# Shell Auto-completion Implementation Plan

## Overview

Add shell auto-completion support for taskfile-help, enabling tab completion for namespaces and task names across multiple shell environments.

## Requirements

- **Shells supported**: bash, tcsh/csh, ksh, zsh, fish
- **Completion targets**: 
  - Namespaces (main, all, dev, test, etc.)
  - Task names within namespaces
  - Command-line flags (--no-color, --search-dirs, etc.)
- **Dynamic discovery**: Completions based on actual Taskfiles in current directory
- **Installation**: Easy setup for each shell

## Implementation Checklist

### Phase 1: Completion Script Generation

- [ ] Add `--completion <shell>` flag to CLI
- [ ] Create `src/taskfile_help/completion.py` module
- [ ] Implement completion script generators:
  - [ ] `generate_bash_completion() -> str`
  - [ ] `generate_zsh_completion() -> str`
  - [ ] `generate_fish_completion() -> str`
  - [ ] `generate_tcsh_completion() -> str`
  - [ ] `generate_ksh_completion() -> str`

### Phase 2: Dynamic Completion Helper

- [ ] Add `--complete <word>` hidden flag for shell callbacks
- [ ] Implement `get_completions(word: str, search_dirs: list[Path]) -> list[str]`:
  - [ ] Discover available namespaces
  - [ ] Return namespace names
  - [ ] Filter by partial match on `word`
  - [ ] Include special namespaces: `main`, `all`

### Phase 3: Task Name Completion

- [ ] Extend `--complete` to support task completion:
  - [ ] Parse format: `--complete <namespace>:<partial_task>`
  - [ ] Load tasks from specified namespace
  - [ ] Return matching task names
  - [ ] Format: `namespace:taskname`

### Phase 4: Flag Completion

- [ ] Complete command-line flags:
  - [ ] `--no-color`
  - [ ] `--search-dirs`
  - [ ] `--json`
  - [ ] `--verbose`
  - [ ] `-s` (short form)
  - [ ] `-h` / `--help`

### Phase 5: Shell-Specific Implementation

#### Bash

- [ ] Generate completion script with `complete -F`
- [ ] Use `COMP_WORDS` and `COMP_CWORD`
- [ ] Call `taskfile-help --complete` for dynamic completions
- [ ] Installation: `~/.bash_completion.d/taskfile-help`

#### Zsh

- [ ] Generate completion script with `compdef`
- [ ] Use `_arguments` for flag completion
- [ ] Use `_values` for namespace completion
- [ ] Installation: `~/.zsh/completion/_taskfile-help`

#### Fish

- [ ] Generate completion script with `complete -c`
- [ ] Use `-a` for dynamic completions
- [ ] Use `-l` and `-s` for flags
- [ ] Installation: `~/.config/fish/completions/taskfile-help.fish`

#### Tcsh/Csh

- [ ] Generate completion script with `complete`
- [ ] Use `p/*/` for position-based completion
- [ ] Call external command for dynamic list
- [ ] Installation: `~/.tcshrc` or `~/.cshrc`

#### Ksh

- [ ] Generate completion script with `set -A`
- [ ] Use `COMP_WORDS` array
- [ ] Installation: `~/.kshrc`

### Phase 6: Installation Helper

- [ ] Add `--install-completion <shell>` command:
  - [ ] Detect shell from `$SHELL` if not specified
  - [ ] Generate completion script
  - [ ] Write to appropriate location
  - [ ] Add source line to shell RC file if needed
  - [ ] Show installation instructions

### Phase 7: Testing

- [ ] Unit tests for `completion.py`:
  - [ ] Test completion script generation for each shell
  - [ ] Test `get_completions()` with various inputs
  - [ ] Test namespace discovery
  - [ ] Test task name completion
  - [ ] Test flag completion

- [ ] Integration tests:
  - [ ] Test `--completion` flag output
  - [ ] Test `--complete` helper with real Taskfiles
  - [ ] Test filtering by partial match

- [ ] Manual testing:
  - [ ] Test in each shell environment
  - [ ] Verify tab completion works
  - [ ] Verify task name completion
  - [ ] Verify flag completion

### Phase 8: Documentation

- [ ] Create `docs/setup/completion.md`:
  - [ ] Installation instructions for each shell
  - [ ] Usage examples
  - [ ] Troubleshooting

- [ ] Update `README.md`:
  - [ ] Add "Shell Completion" section
  - [ ] Link to detailed docs

- [ ] Update `--help` output:
  - [ ] Document `--completion` flag
  - [ ] Document `--install-completion` command

## Code Structure

```
src/taskfile_help/
├── completion.py         # NEW: Completion logic
├── taskfile_help.py      # MODIFIED: Add completion flags
└── discovery.py          # EXISTING: Used for namespace discovery

tests/
├── unit/
│   └── test_completion.py # NEW: Completion tests
└── e2e/
    └── test_cli.py        # MODIFIED: Add completion tests

docs/
└── setup/
    └── completion.md      # NEW: Completion documentation
```

## Example Implementation

### completion.py

```python
"""Shell completion support."""

from pathlib import Path
from .discovery import TaskfileDiscovery
from .parser import parse_taskfile
from .output import TextOutputter


def get_completions(word: str, search_dirs: list[Path]) -> list[str]:
    """Get completion suggestions for a word.
    
    Args:
        word: Partial word to complete
        search_dirs: Directories to search for Taskfiles
        
    Returns:
        List of completion suggestions
    """
    completions = []
    
    # Check if completing a task name (format: namespace:task)
    if ':' in word:
        namespace, partial_task = word.split(':', 1)
        completions.extend(_complete_task_name(namespace, partial_task, search_dirs))
    else:
        # Complete namespace
        completions.extend(_complete_namespace(word, search_dirs))
    
    return sorted(completions)


def _complete_namespace(partial: str, search_dirs: list[Path]) -> list[str]:
    """Complete namespace names."""
    discovery = TaskfileDiscovery(search_dirs)
    namespaces = ['main', 'all']
    
    # Add discovered namespaces
    for ns, _ in discovery.get_all_namespace_taskfiles():
        namespaces.append(ns)
    
    # Filter by partial match
    return [ns for ns in namespaces if ns.startswith(partial)]


def _complete_task_name(namespace: str, partial: str, search_dirs: list[Path]) -> list[str]:
    """Complete task names within a namespace."""
    discovery = TaskfileDiscovery(search_dirs)
    
    # Find taskfile
    if namespace in ('', 'main'):
        taskfile = discovery.find_main_taskfile()
    else:
        taskfile = discovery.find_namespace_taskfile(namespace)
    
    if not taskfile:
        return []
    
    # Parse tasks
    outputter = TextOutputter()
    tasks = parse_taskfile(taskfile, namespace, outputter)
    
    # Extract task names and filter
    task_names = [task_name for _, task_name, _ in tasks]
    matches = [f"{namespace}:{name}" for name in task_names if name.startswith(partial)]
    
    return matches


def generate_bash_completion() -> str:
    """Generate bash completion script."""
    return '''
_taskfile_help_completion() {
    local cur prev words cword
    _init_completion || return
    
    case "$prev" in
        --search-dirs|-s)
            _filedir -d
            return
            ;;
        --completion|--install-completion)
            COMPREPLY=($(compgen -W "bash zsh fish tcsh ksh" -- "$cur"))
            return
            ;;
    esac
    
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W "--no-color --search-dirs --json --verbose --help --completion --install-completion" -- "$cur"))
        return
    fi
    
    # Get dynamic completions
    local completions=$(taskfile-help --complete "$cur" 2>/dev/null)
    COMPREPLY=($(compgen -W "$completions" -- "$cur"))
}

complete -F _taskfile_help_completion taskfile-help
'''


def generate_zsh_completion() -> str:
    """Generate zsh completion script."""
    return '''
#compdef taskfile-help

_taskfile_help() {
    local -a namespaces tasks flags
    
    flags=(
        '--no-color[Disable colored output]'
        '--search-dirs[Directories to search]:directory:_directories'
        '--json[Output in JSON format]'
        '--verbose[Show verbose output]'
        '--help[Show help message]'
        '--completion[Generate completion script]:shell:(bash zsh fish tcsh ksh)'
        '--install-completion[Install completion script]:shell:(bash zsh fish tcsh ksh)'
    )
    
    # Get dynamic completions
    local completions=(${(f)"$(taskfile-help --complete ${words[CURRENT]} 2>/dev/null)"})
    
    _arguments -s $flags && return 0
    _describe 'namespace or task' completions
}

_taskfile_help "$@"
'''


def generate_fish_completion() -> str:
    """Generate fish completion script."""
    return '''
# Disable file completion
complete -c taskfile-help -f

# Flags
complete -c taskfile-help -l no-color -d "Disable colored output"
complete -c taskfile-help -l search-dirs -s s -d "Directories to search" -r -F
complete -c taskfile-help -l json -d "Output in JSON format"
complete -c taskfile-help -l verbose -d "Show verbose output"
complete -c taskfile-help -l help -s h -d "Show help message"
complete -c taskfile-help -l completion -d "Generate completion script" -xa "bash zsh fish tcsh ksh"
complete -c taskfile-help -l install-completion -d "Install completion script" -xa "bash zsh fish tcsh ksh"

# Dynamic namespace and task completion
complete -c taskfile-help -a "(taskfile-help --complete (commandline -ct) 2>/dev/null)"
'''


def generate_tcsh_completion() -> str:
    """Generate tcsh/csh completion script."""
    return '''
# Tcsh completion for taskfile-help
complete taskfile-help 'p/1/`taskfile-help --complete "" 2>/dev/null`/'
'''


def generate_ksh_completion() -> str:
    """Generate ksh completion script."""
    return '''
# Ksh completion for taskfile-help
function _taskfile_help_complete {
    typeset -a completions
    completions=($(taskfile-help --complete "${COMP_WORDS[COMP_CWORD]}" 2>/dev/null))
    COMPREPLY=("${completions[@]}")
}

set -A complete_taskfile_help _taskfile_help_complete
'''
```

### Modified taskfile_help.py

```python
def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    # ... existing arg parsing ...
    
    # Handle completion commands
    if hasattr(args, 'completion') and args.completion:
        from .completion import (
            generate_bash_completion,
            generate_zsh_completion,
            generate_fish_completion,
            generate_tcsh_completion,
            generate_ksh_completion,
        )
        
        generators = {
            'bash': generate_bash_completion,
            'zsh': generate_zsh_completion,
            'fish': generate_fish_completion,
            'tcsh': generate_tcsh_completion,
            'ksh': generate_ksh_completion,
        }
        
        if args.completion in generators:
            print(generators[args.completion]())
            return 0
        else:
            print(f"Unknown shell: {args.completion}", file=sys.stderr)
            return 1
    
    if hasattr(args, 'complete') and args.complete is not None:
        from .completion import get_completions
        completions = get_completions(args.complete, config.discovery.search_dirs)
        print('\n'.join(completions))
        return 0
    
    # ... rest of existing logic ...
```

## Installation Examples

### Bash

```bash
# Generate and install
taskfile-help --install-completion bash

# Or manually
taskfile-help --completion bash > ~/.bash_completion.d/taskfile-help
echo 'source ~/.bash_completion.d/taskfile-help' >> ~/.bashrc
```

### Zsh

```bash
# Generate and install
taskfile-help --install-completion zsh

# Or manually
mkdir -p ~/.zsh/completion
taskfile-help --completion zsh > ~/.zsh/completion/_taskfile-help
echo 'fpath=(~/.zsh/completion $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
```

### Fish

```bash
# Generate and install
taskfile-help --install-completion fish

# Or manually
mkdir -p ~/.config/fish/completions
taskfile-help --completion fish > ~/.config/fish/completions/taskfile-help.fish
```

## Success Criteria

- [ ] Tab completion works in all 5 shells
- [ ] Namespace completion is dynamic
- [ ] Task name completion works with `namespace:<TAB>`
- [ ] Flag completion works
- [ ] Installation is simple and documented
- [ ] No performance impact on normal usage
- [ ] Completions update when Taskfiles change
