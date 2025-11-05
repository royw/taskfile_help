from pathlib import Path
import re
from typing import Any

import yaml


class TaskfileDiscovery:
    """Handles discovery and resolution of Taskfile paths."""

    # Supported file extensions
    EXTENSIONS = [".yml", ".yaml"]

    # Naming patterns for namespace taskfiles
    NAMESPACE_PATTERNS = ["Taskfile-{}", "Taskfile_{}"]

    # Main taskfile names (order matters - first match wins)
    MAIN_NAMES = [
        "Taskfile.yml",
        "Taskfile.yaml",
        "taskfile.yml",
        "taskfile.yaml",
        "Taskfile.dist.yml",
        "Taskfile.dist.yaml",
        "taskfile.dist.yml",
        "taskfile.dist.yaml",
    ]

    # Regex pattern to match main taskfiles (for reference): ^[Tt]askfile(\.dist)?\.ya?ml$

    # Regex pattern to match namespace taskfiles and extract namespace
    NAMESPACE_REGEX = re.compile(r"^[Tt]askfile[-_](?P<namespace>\w+)\.ya?ml$")

    def __init__(self, search_dirs: list[Path]) -> None:
        """Initialize with search directories.

        Args:
            search_dirs: List of directories to search for taskfiles
        """
        self.search_dirs = search_dirs
        self._includes_cache: dict[str, Path] | None = None

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

        First checks the includes section from the main Taskfile.
        Falls back to filename-based search if not found in includes.

        Args:
            namespace: The namespace to search for (e.g., 'rag', 'dev')

        Returns:
            Path to namespace Taskfile if found, None otherwise
        """
        # Use cached includes if available
        if self._includes_cache is None:
            self._includes_cache = self._parse_includes_from_main_taskfile() or {}

        # Check includes first
        if self._includes_cache and namespace in self._includes_cache:
            return self._includes_cache[namespace]

        # Fall back to filename-based search
        for search_dir in self.search_dirs:
            for pattern in self.NAMESPACE_PATTERNS:
                for ext in self.EXTENSIONS:
                    filename = pattern.format(namespace) + ext
                    path = search_dir / filename
                    if path.exists():
                        return path
        return None

    def _parse_includes_from_taskfile(
        self,
        taskfile_path: Path,
        namespace_prefix: str = "",
        visited: set[Path] | None = None,
    ) -> dict[str, Path]:
        """Recursively parse includes from a taskfile.

        Args:
            taskfile_path: Path to the taskfile to parse (should be absolute)
            namespace_prefix: Prefix to prepend to namespace names (e.g., "foo:bar")
            visited: Set of visited absolute paths in the current recursion chain to prevent cycles

        Returns:
            Dictionary mapping full namespace paths to their taskfile paths
        """
        if visited is None:
            visited = set()

        # Ensure we're working with absolute resolved paths for cycle detection
        taskfile_path = taskfile_path.resolve()

        # Prevent infinite recursion - check if this path is already in the current chain
        if taskfile_path in visited:
            return {}

        # Add to visited set for this recursion branch
        visited = visited | {taskfile_path}  # Create new set to avoid modifying parent's set

        namespace_map: dict[str, Path] = {}

        try:
            with open(taskfile_path, encoding="utf-8") as f:
                data: dict[str, Any] = yaml.safe_load(f) or {}
                includes: dict[str, Any] = data.get("includes", {})

                if not includes:
                    return {}

                taskfile_dir = taskfile_path.parent

                for namespace, include_config in includes.items():
                    # Build the full namespace path
                    full_namespace = f"{namespace_prefix}:{namespace}" if namespace_prefix else namespace

                    # Extract the taskfile path from the config
                    included_taskfile_path: str | None = None
                    if isinstance(include_config, dict):
                        included_taskfile_path = include_config.get("taskfile")
                    elif isinstance(include_config, str):
                        included_taskfile_path = include_config

                    if included_taskfile_path:
                        # Resolve path relative to current taskfile's directory
                        resolved_path = (taskfile_dir / included_taskfile_path).resolve()
                        if resolved_path.exists() and resolved_path not in visited:
                            # Only add if not already in the visited chain (prevents cycles)
                            namespace_map[full_namespace] = resolved_path

                            # Recursively parse includes from the included taskfile
                            # Pass the updated visited set that includes current path
                            nested_includes = self._parse_includes_from_taskfile(
                                resolved_path,
                                full_namespace,
                                visited,  # This already includes taskfile_path
                            )
                            namespace_map.update(nested_includes)

        except Exception:  # noqa: S110
            # If parsing fails, just return what we have so far
            # We silently ignore errors to allow partial results and maintain backward compatibility
            pass

        return namespace_map

    def _parse_includes_from_main_taskfile(self) -> dict[str, Path] | None:
        """Parse the includes section from the main Taskfile recursively.

        Returns:
            Dictionary mapping namespace names to their taskfile paths,
            or None if main Taskfile doesn't exist or has no includes
        """
        main_taskfile = self.find_main_taskfile()
        if not main_taskfile:
            return None

        namespace_map = self._parse_includes_from_taskfile(main_taskfile)
        return namespace_map if namespace_map else None

    def _find_namespace_taskfiles_in_dir(self, search_dir: Path, taskfiles: dict[str, Path]) -> None:
        """Find namespace taskfiles in a single directory using filename regex.

        This is a fallback method when includes section is not available.

        Args:
            search_dir: Directory to search in
            taskfiles: Dictionary to update with found taskfiles (namespace -> path)
        """
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

    def get_all_namespace_taskfiles(self) -> list[tuple[str, Path]]:
        """Find all namespace Taskfiles.

        First tries to parse the includes section from the main Taskfile.
        Falls back to filename-based discovery if includes are not available.

        Returns:
            List of (namespace, path) tuples sorted by namespace
        """
        # Use cached includes if available
        if self._includes_cache is None:
            self._includes_cache = self._parse_includes_from_main_taskfile() or {}

        # If we have includes from main Taskfile, use those
        if self._includes_cache:
            return sorted(self._includes_cache.items(), key=lambda x: x[0])

        # Otherwise, fall back to filename-based discovery
        taskfiles: dict[str, Path] = {}
        for search_dir in self.search_dirs:
            if search_dir.exists():
                self._find_namespace_taskfiles_in_dir(search_dir, taskfiles)

        # Return sorted by namespace
        return sorted(taskfiles.items(), key=lambda x: x[0])

    def _get_namespace_possible_paths(self, search_dir: Path, namespace: str) -> list[Path]:
        """Get all possible paths for a namespace in a directory.

        Args:
            search_dir: Directory to search in
            namespace: The namespace to get paths for

        Returns:
            List of possible paths for the namespace
        """
        paths = []
        for pattern in self.NAMESPACE_PATTERNS:
            for ext in self.EXTENSIONS:
                filename = pattern.format(namespace) + ext
                paths.append(search_dir / filename)
        return paths

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
                paths.extend(self._get_namespace_possible_paths(search_dir, namespace))
        return paths
