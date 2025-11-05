from pathlib import Path
from typing import Any

import yaml


class TaskfileDiscovery:
    """Handles discovery and resolution of Taskfile paths."""

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
        """Find a Taskfile for a specific namespace from the includes section.

        Args:
            namespace: The namespace to search for (e.g., 'dev', 'foo:bar')

        Returns:
            Path to namespace Taskfile if found, None otherwise
        """
        # Use cached includes if available
        if self._includes_cache is None:
            self._includes_cache = self._parse_includes_from_main_taskfile() or {}

        # Return the namespace from includes
        return self._includes_cache.get(namespace) if self._includes_cache else None

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

        # Add to visited set for this recursion branch
        # Note: Circular references are prevented by the caller checking visited before recursing
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

    def get_all_namespace_taskfiles(self) -> list[tuple[str, Path]]:
        """Find all namespace Taskfiles from the includes section.

        Returns:
            List of (namespace, path) tuples sorted by namespace
        """
        # Use cached includes if available
        if self._includes_cache is None:
            self._includes_cache = self._parse_includes_from_main_taskfile() or {}

        # Return includes from main Taskfile
        return sorted(self._includes_cache.items(), key=lambda x: x[0]) if self._includes_cache else []

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
        return paths
