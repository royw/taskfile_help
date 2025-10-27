from collections.abc import Callable
import json
import sys
from typing import Any, Protocol


# Task column width for formatting
TASK_COLUMN_WIDTH = 20


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"

    @classmethod
    def disable(cls) -> None:
        """Disable all colors (for piped output)."""
        cls.RESET = ""
        cls.BOLD = ""
        cls.CYAN = ""
        cls.GREEN = ""
        cls.RED = ""
        cls.YELLOW = ""


class Outputter(Protocol):
    """Protocol for outputting taskfile information."""

    def output_single(
        self,
        namespace: str,
        tasks: list[tuple[str, str, str]],
        output_fn: Callable[..., Any] = print,
    ) -> None:
        """Output tasks for a single namespace.

        Args:
            namespace: The namespace (e.g., 'rag', 'dev', or '' for main)
            tasks: List of (group, task_name, description) tuples
            output_fn: Function to use for output (default: print)
        """
        ...

    def output_all(
        self,
        taskfiles: list[tuple[str, list[tuple[str, str, str]]]],
        output_fn: Callable[..., Any] = print,
    ) -> None:
        """Output tasks for all taskfiles.

        Args:
            taskfiles: List of (namespace, tasks) tuples
            output_fn: Function to use for output (default: print)
        """
        ...

    def output_heading(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a heading."""
        ...

    def output_message(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a message."""
        ...

    def output_error(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output an error message."""
        ...

    def output_warning(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a warning message."""
        ...


class TextOutputter:
    """Text-based outputter with color support."""

    def output_single(
        self,
        namespace: str,
        tasks: list[tuple[str, str, str]],
        output_fn: Callable[..., Any] = print,
    ) -> None:
        """Output tasks for a single namespace in text format.

        Args:
            namespace: The namespace (e.g., 'rag', 'dev', or '' for main)
            tasks: List of (group, task_name, description) tuples
            output_fn: Function to use for output (default: print)
        """
        if not tasks:
            output_fn(f"{Colors.YELLOW}No public tasks found for namespace '{namespace}'{Colors.RESET}")
            return

        # Print header
        title = f"{namespace.upper()} Task Commands" if namespace else "Task Commands"
        output_fn(f"{Colors.BOLD}{Colors.CYAN}{title}:{Colors.RESET}")
        output_fn("")

        # Group tasks by their group name
        grouped: dict[str, list[tuple[str, str]]] = {}
        for group, task_name, desc in tasks:
            if group not in grouped:
                grouped[group] = []
            grouped[group].append((task_name, desc))

        # Print each group
        for group, group_tasks in grouped.items():
            # Print group header
            output_fn(f"{Colors.BOLD}{Colors.GREEN}{group}:{Colors.RESET}")

            # Print tasks in this group
            for task_name, desc in group_tasks:
                full_task = f"{namespace}:{task_name}" if namespace else task_name
                output_fn(f"  {Colors.CYAN}task {full_task:<{TASK_COLUMN_WIDTH}}{Colors.RESET} - {desc}")

            output_fn("")

    def output_all(
        self,
        taskfiles: list[tuple[str, list[tuple[str, str, str]]]],
        output_fn: Callable[..., Any] = print,
    ) -> None:
        """Output tasks for all taskfiles in text format.

        Args:
            taskfiles: List of (namespace, tasks) tuples
            output_fn: Function to use for output (default: print)
        """
        for namespace, tasks in taskfiles:
            if namespace:
                output_fn(f"{Colors.CYAN}{Colors.BOLD}=== {namespace.upper()} Taskfile ==={Colors.RESET}\n")
            else:
                output_fn(f"{Colors.CYAN}{Colors.BOLD}=== Main Taskfile ==={Colors.RESET}\n")
            self.output_single(namespace, tasks, output_fn)
            output_fn("")

    def output_heading(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a heading."""
        output_fn(f"{Colors.CYAN}{message}{Colors.RESET}")

    def output_message(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a message."""
        output_fn(message)

    def output_error(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output an error message."""
        output_fn(f"{Colors.RED}Error: {message}{Colors.RESET}", file=sys.stderr)

    def output_warning(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a warning message."""
        output_fn(f"{Colors.YELLOW}Warning: {message}{Colors.RESET}", file=sys.stderr)


class JsonOutputter:
    """JSON-based outputter."""

    def output_single(
        self,
        namespace: str,
        tasks: list[tuple[str, str, str]],
        output_fn: Callable[..., Any] = print,
    ) -> None:
        """Output tasks for a single namespace in JSON format.

        Args:
            namespace: The namespace (e.g., 'rag', 'dev', or '' for main)
            tasks: List of (group, task_name, description) tuples
            output_fn: Function to use for output (default: print)
        """
        output = {
            "namespace": namespace,
            "tasks": [
                {
                    "group": group,
                    "name": task_name,
                    "full_name": f"{namespace}:{task_name}" if namespace else task_name,
                    "description": desc,
                }
                for group, task_name, desc in tasks
            ],
        }
        output_fn(json.dumps(output, indent=2))

    def output_all(
        self,
        taskfiles: list[tuple[str, list[tuple[str, str, str]]]],
        output_fn: Callable[..., Any] = print,
    ) -> None:
        """Output tasks for all taskfiles in JSON format.

        Args:
            taskfiles: List of (namespace, tasks) tuples
            output_fn: Function to use for output (default: print)
        """
        output = {
            "taskfiles": [
                {
                    "namespace": namespace,
                    "tasks": [
                        {
                            "group": group,
                            "name": task_name,
                            "full_name": f"{namespace}:{task_name}" if namespace else task_name,
                            "description": desc,
                        }
                        for group, task_name, desc in tasks
                    ],
                }
                for namespace, tasks in taskfiles
            ]
        }
        output_fn(json.dumps(output, indent=2))

    def output_heading(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a heading."""
        output_fn(message)

    def output_message(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a message."""
        output_fn(message)

    def output_error(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output an error message."""
        output = {"error": message}
        output_fn(json.dumps(output), file=sys.stderr)

    def output_warning(self, message: str, output_fn: Callable[..., Any] = print) -> None:
        """Output a warning message."""
        output = {"warning": message}
        output_fn(json.dumps(output), file=sys.stderr)
