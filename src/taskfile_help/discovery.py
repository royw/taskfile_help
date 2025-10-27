from pathlib import Path


class TaskfileDiscovery:
    """Handles discovery and resolution of Taskfile paths."""

    # Supported file extensions
    EXTENSIONS = [".yml", ".yaml"]

    # Naming patterns for namespace taskfiles
    NAMESPACE_PATTERNS = ["Taskfile-{}", "Taskfile_{}"]

    # Main taskfile names
    MAIN_NAMES = ["Taskfile.yml", "Taskfile.yaml"]

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
        taskfiles: list[tuple[str, Path]] = []

        # Search for all namespace patterns in all search directories
        for search_dir in self.search_dirs:
            for pattern in self.NAMESPACE_PATTERNS:
                for ext in self.EXTENSIONS:
                    glob_pattern = pattern.format("*") + ext
                    for path in sorted(search_dir.glob(glob_pattern)):
                        # Extract namespace from filename
                        stem = path.stem
                        for pat in self.NAMESPACE_PATTERNS:
                            prefix = pat.format("").rstrip("_").rstrip("-")
                            if stem.startswith(prefix):
                                # Remove prefix and separator
                                namespace = stem.removeprefix(prefix + "_").removeprefix(prefix + "-")
                                if namespace:  # Ensure we got a valid namespace
                                    taskfiles.append((namespace, path))
                                break

        # Remove duplicates and sort by namespace (dict preserves insertion order in Python 3.7+)
        unique_dict = dict(sorted(taskfiles, key=lambda x: x[0]))
        return list(unique_dict.items())

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
