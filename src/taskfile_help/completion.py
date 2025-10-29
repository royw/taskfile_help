"""Shell completion support for taskfile-help."""

from __future__ import annotations

import os
from pathlib import Path

from .discovery import TaskfileDiscovery
from .output import TextOutputter
from .parser import parse_taskfile


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
    if ":" in word:
        namespace, partial_task = word.split(":", 1)
        completions.extend(_complete_task_name(namespace, partial_task, search_dirs))
    else:
        # Complete namespace
        completions.extend(_complete_namespace(word, search_dirs))
        # Also include flags if word starts with -
        if word.startswith("-"):
            completions.extend(_complete_flags(word))

    return sorted(set(completions))


def _complete_namespace(partial: str, search_dirs: list[Path]) -> list[str]:
    """Complete namespace names.

    Args:
        partial: Partial namespace to complete
        search_dirs: Directories to search for Taskfiles

    Returns:
        List of matching namespace names
    """
    discovery = TaskfileDiscovery(search_dirs)
    namespaces = ["main", "all"]

    # Add discovered namespaces
    for ns, _ in discovery.get_all_namespace_taskfiles():
        namespaces.append(ns)

    # Filter by partial match
    return [ns for ns in namespaces if ns.startswith(partial)]


def _complete_task_name(namespace: str, partial: str, search_dirs: list[Path]) -> list[str]:
    """Complete task names within a namespace.

    Args:
        namespace: Namespace to search in
        partial: Partial task name to complete
        search_dirs: Directories to search for Taskfiles

    Returns:
        List of matching task names in format "namespace:taskname"
    """
    discovery = TaskfileDiscovery(search_dirs)

    # Find taskfile
    if namespace in ("", "main"):
        taskfile = discovery.find_main_taskfile()
        namespace = ""  # Use empty namespace for main
    else:
        taskfile = discovery.find_namespace_taskfile(namespace)

    if not taskfile:
        return []

    # Parse tasks
    outputter = TextOutputter()
    try:
        tasks = parse_taskfile(taskfile, namespace, outputter)
    except Exception:
        # Defensive: parse_taskfile shouldn't raise, but ensure completion never crashes
        return []

    # Extract task names and filter
    task_names = [task_name for _, task_name, _ in tasks]
    if namespace:
        matches = [f"{namespace}:{name}" for name in task_names if name.startswith(partial)]
    else:
        matches = [name for name in task_names if name.startswith(partial)]

    return matches


def _complete_flags(partial: str) -> list[str]:
    """Complete command-line flags.

    Args:
        partial: Partial flag to complete

    Returns:
        List of matching flags
    """
    flags = [
        "--no-color",
        "--search-dirs",
        "--json",
        "--verbose",
        "--help",
        "--completion",
        "--install-completion",
        "--complete",
        "-s",
        "-v",
        "-h",
    ]
    return [flag for flag in flags if flag.startswith(partial)]


def generate_bash_completion() -> str:
    """Generate bash completion script.

    Returns:
        Bash completion script as a string
    """
    return """# Bash completion for taskfile-help
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
        local flags="--no-color --search-dirs --json --verbose --help"
        flags="$flags --completion --install-completion -s -v -h"
        COMPREPLY=($(compgen -W "$flags" -- "$cur"))
        return
    fi

    # Get dynamic completions
    local completions=$(taskfile-help --complete "$cur" 2>/dev/null)
    COMPREPLY=($(compgen -W "$completions" -- "$cur"))
}

complete -F _taskfile_help_completion taskfile-help
"""


def generate_zsh_completion() -> str:
    """Generate zsh completion script.

    Returns:
        Zsh completion script as a string
    """
    return """#compdef taskfile-help

_taskfile_help() {
    local -a namespaces tasks flags

    flags=(
        '--no-color[Disable colored output]'
        '--search-dirs[Directories to search]:directory:_directories'
        '-s[Directories to search]:directory:_directories'
        '--json[Output in JSON format]'
        '--verbose[Show verbose output]'
        '-v[Show verbose output]'
        '--help[Show help message]'
        '-h[Show help message]'
        '--completion[Generate completion script]:shell:(bash zsh fish tcsh ksh)'
        '--install-completion[Install completion script]:shell:(bash zsh fish tcsh ksh)'
    )

    # Get dynamic completions
    local completions=(${(f)"$(taskfile-help --complete ${words[CURRENT]} 2>/dev/null)"})

    _arguments -s $flags && return 0
    _describe 'namespace or task' completions
}

_taskfile_help "$@"
"""


def generate_fish_completion() -> str:
    """Generate fish completion script.

    Returns:
        Fish completion script as a string
    """
    return """# Fish completion for taskfile-help

# Disable file completion
complete -c taskfile-help -f

# Flags
complete -c taskfile-help -l no-color -d "Disable colored output"
complete -c taskfile-help -l search-dirs -s s -d "Directories to search" -r -F
complete -c taskfile-help -l json -d "Output in JSON format"
complete -c taskfile-help -l verbose -s v -d "Show verbose output"
complete -c taskfile-help -l help -s h -d "Show help message"
complete -c taskfile-help -l completion -d "Generate completion script" -xa "bash zsh fish tcsh ksh"
complete -c taskfile-help -l install-completion -d "Install completion script" -xa "bash zsh fish tcsh ksh"

# Dynamic namespace and task completion
complete -c taskfile-help -a "(taskfile-help --complete (commandline -ct) 2>/dev/null)"
"""


def generate_tcsh_completion() -> str:
    """Generate tcsh/csh completion script.

    Returns:
        Tcsh completion script as a string
    """
    return """# Tcsh completion for taskfile-help
complete taskfile-help 'p/1/`taskfile-help --complete "" 2>/dev/null`/'
"""


def generate_ksh_completion() -> str:
    """Generate ksh completion script.

    Returns:
        Ksh completion script as a string
    """
    return """# Ksh completion for taskfile-help
function _taskfile_help_complete {
    typeset -a completions
    completions=($(taskfile-help --complete "${COMP_WORDS[COMP_CWORD]}" 2>/dev/null))
    COMPREPLY=("${completions[@]}")
}

set -A complete_taskfile_help _taskfile_help_complete
"""


def install_completion(shell: str | None = None) -> tuple[bool, str]:
    """Install completion script for the specified shell.

    Args:
        shell: Shell name (bash, zsh, fish, tcsh, ksh). If None, auto-detect from $SHELL

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Auto-detect shell if not specified
    if shell is None:
        shell_path = os.environ.get("SHELL", "")
        shell = Path(shell_path).name if shell_path else None

    if not shell:
        return False, "Could not detect shell. Please specify shell explicitly: --install-completion <shell>"

    # Normalize shell name
    shell = shell.lower()
    if shell not in ("bash", "zsh", "fish", "tcsh", "csh", "ksh"):
        return False, f"Unsupported shell: {shell}. Supported shells: bash, zsh, fish, tcsh, ksh"

    # Handle csh as tcsh
    if shell == "csh":
        shell = "tcsh"

    # Generate completion script
    generators = {
        "bash": generate_bash_completion,
        "zsh": generate_zsh_completion,
        "fish": generate_fish_completion,
        "tcsh": generate_tcsh_completion,
        "ksh": generate_ksh_completion,
    }

    script = generators[shell]()

    # Determine installation path
    home = Path.home()
    install_paths = {
        "bash": home / ".bash_completion.d" / "taskfile-help",
        "zsh": home / ".zsh" / "completion" / "_taskfile-help",
        "fish": home / ".config" / "fish" / "completions" / "taskfile-help.fish",
        "tcsh": home / ".tcshrc.d" / "taskfile-help.tcsh",
        "ksh": home / ".kshrc.d" / "taskfile-help.ksh",
    }

    install_path = install_paths[shell]

    # Create directory if it doesn't exist
    install_path.parent.mkdir(parents=True, exist_ok=True)

    # Write completion script
    try:
        install_path.write_text(script)
    except Exception as e:
        return False, f"Failed to write completion script: {e}"

    # Generate instructions for sourcing
    instructions = _get_sourcing_instructions(shell, install_path)

    return True, f"Completion script installed to: {install_path}\n\n{instructions}"


def _get_sourcing_instructions(shell: str, install_path: Path) -> str:
    """Get instructions for sourcing the completion script.

    Args:
        shell: Shell name
        install_path: Path where completion script was installed

    Returns:
        Instructions as a string
    """
    if shell == "bash":
        rc_file = "~/.bashrc"
        return f"""To enable completions, add this line to your {rc_file}:

    source {install_path}

Then reload your shell or run: source {rc_file}"""

    elif shell == "zsh":
        rc_file = "~/.zshrc"
        completion_dir = install_path.parent
        return f"""To enable completions, add these lines to your {rc_file}:

    fpath=({completion_dir} $fpath)
    autoload -Uz compinit && compinit

Then reload your shell or run: source {rc_file}"""

    elif shell == "fish":
        return """Fish will automatically load completions from ~/.config/fish/completions/

Reload your shell or run: source ~/.config/fish/config.fish"""

    elif shell == "tcsh":
        rc_file = "~/.tcshrc"
        return f"""To enable completions, add this line to your {rc_file}:

    source {install_path}

Then reload your shell or run: source {rc_file}"""

    elif shell == "ksh":
        rc_file = "~/.kshrc"
        return f"""To enable completions, add this line to your {rc_file}:

    . {install_path}

Then reload your shell or run: . {rc_file}"""

    else:
        # This should never happen due to validation in install_completion()
        return f"Unsupported shell: {shell}"
