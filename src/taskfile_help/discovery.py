from pathlib import Path
import re


class TaskfileDiscovery:
    """Handles discovery and resolution of Taskfile paths."""

    # Supported file extensions
    EXTENSIONS = [".yml", ".yaml"]

    # Naming patterns for namespace taskfiles
    NAMESPACE_PATTERNS = ["Taskfile-{}", "Taskfile_{}"]

    # Main taskfile names (order matters - first match wins)
    MAIN_NAMES = ["Taskfile.yml", "Taskfile.yaml", "taskfile.yml", "taskfile.yaml"]

    # Regex pattern to match main taskfiles (for reference): ^[Tt]askfile\.ya?ml$

    # Regex pattern to match namespace taskfiles and extract namespace
    NAMESPACE_REGEX = re.compile(r"^[Tt]askfile[-_](?P<namespace>\w+)\.ya?ml$")

    def __init__(self, search_dirs: list[Path]) -> None:
        """Initialize with search directories.

        Args:
            search_dirs: List of directories to search for taskfiles
        """
        self.search_dirs = search_dirs

    def find_main_taskfile(self) -> Path | None:
        """Find the main Taskfile in the search directories.

        Returns:
            Path to main Taskfile if found, None otherwise
        """
        for search_dir in self.search_dirs:
            for name in self.MAIN_NAMES:
                path = search_dir / name
                if path.exists():
                    return path
        return None

    def find_namespace_taskfile(self, namespace: str) -> Path | None:
        """Find a Taskfile for a specific namespace.

        Args:
            namespace: The namespace to search for (e.g., 'rag', 'dev')

        Returns:
            Path to namespace Taskfile if found, None otherwise
        """
        for search_dir in self.search_dirs:
            for pattern in self.NAMESPACE_PATTERNS:
                for ext in self.EXTENSIONS:
                    filename = pattern.format(namespace) + ext
                    path = search_dir / filename
                    if path.exists():
                        return path
        return None

    def get_all_namespace_taskfiles(self) -> list[tuple[str, Path]]:
        """Find all namespace Taskfiles in the search directories.

        Returns:
            List of (namespace, path) tuples sorted by namespace
        """
        taskfiles: dict[str, Path] = {}

        # Search for all taskfiles matching the namespace pattern
        for search_dir in self.search_dirs:
            if not search_dir.exists():
                continue

            for path in search_dir.iterdir():
                if not path.is_file():
                    continue

                # Try to match the filename against the namespace pattern
                match = self.NAMESPACE_REGEX.match(path.name)
                if match:
                    namespace = match.group("namespace")
                    # Only add if not already found (first match wins)
                    if namespace not in taskfiles:
                        taskfiles[namespace] = path

        # Return sorted by namespace
        return sorted(taskfiles.items(), key=lambda x: x[0])

    def get_possible_paths(self, namespace: str) -> list[Path]:
        """Get all possible paths for a namespace (for error messages).

        Args:
            namespace: The namespace to get paths for

        Returns:
            List of possible paths that were checked
        """
        paths = []
        for search_dir in self.search_dirs:
            if not namespace or namespace == "main":
                paths.extend([search_dir / name for name in self.MAIN_NAMES])
            else:
                for pattern in self.NAMESPACE_PATTERNS:
                    for ext in self.EXTENSIONS:
                        filename = pattern.format(namespace) + ext
                        paths.append(search_dir / filename)
        return paths
