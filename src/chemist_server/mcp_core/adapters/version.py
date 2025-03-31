"""Version control for tool adapters."""

from enum import Enum

from pydantic import BaseModel

from ..errors import AdapterError


class VersionStrategy(str, Enum):
    """Strategy for versioning tools."""

    SEMANTIC = "semantic"  # Semantic versioning (e.g., 1.2.3)
    DATE = "date"  # Date-based versioning (e.g., 20230401)
    INCREMENT = "increment"  # Simple incremental versioning (e.g., 1, 2, 3)


class VersionInfo(BaseModel):
    """Version information for a tool."""

    version: str
    released_at: str  # ISO format date
    is_latest: bool = False
    is_deprecated: bool = False
    min_core_version: str | None = None
    changes: list[str] = []
    metadata: dict[str, str] = {}


class VersionManager:
    """Manages versioning for tool adapters."""

    def __init__(
        self, strategy: VersionStrategy | str = VersionStrategy.SEMANTIC
    ) -> None:
        """Initialize version manager.

        Args:
            strategy: Versioning strategy to use
        """
        if isinstance(strategy, str):
            try:
                self.strategy = VersionStrategy(strategy)
            except ValueError as err:
                raise AdapterError(f"Invalid version strategy: {strategy}") from err
        else:
            self.strategy = strategy

        self.versions: dict[str, dict[str, VersionInfo]] = {}

    def register_version(self, tool_name: str, version_info: VersionInfo) -> None:
        """Register a version for a tool.

        Args:
            tool_name: Name of the tool
            version_info: Version information

        Raises:
            AdapterError: If version is invalid or already registered
        """
        if tool_name not in self.versions:
            self.versions[tool_name] = {}

        if version_info.version in self.versions[tool_name]:
            raise AdapterError(
                f"Version {version_info.version} already registered for tool {tool_name}"
            )

        # Validate according to strategy
        self._validate_version(version_info.version)

        # If this is marked as latest, unmark any other latest versions
        if version_info.is_latest:
            for other_version in self.versions[tool_name].values():
                other_version.is_latest = False

        self.versions[tool_name][version_info.version] = version_info

    def get_latest_version(self, tool_name: str) -> str:
        """Get the latest version for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            str: Latest version string

        Raises:
            AdapterError: If tool has no registered versions
        """
        if tool_name not in self.versions or not self.versions[tool_name]:
            raise AdapterError(f"No versions registered for tool {tool_name}")

        # First check for explicitly marked latest
        for version, info in self.versions[tool_name].items():
            if info.is_latest:
                return version

        # Otherwise use strategy-specific logic
        if self.strategy == VersionStrategy.SEMANTIC:
            return max(
                self.versions[tool_name].keys(),
                key=lambda v: [int(x) for x in v.split(".")],
            )
        elif self.strategy == VersionStrategy.DATE:
            return max(self.versions[tool_name].keys())
        elif self.strategy == VersionStrategy.INCREMENT:
            return max(self.versions[tool_name].keys(), key=lambda v: int(v))

        # Fallback
        return max(self.versions[tool_name].keys())

    def get_version_info(self, tool_name: str, version: str) -> VersionInfo:
        """Get version info for a tool.

        Args:
            tool_name: Name of the tool
            version: Version string

        Returns:
            VersionInfo: Version information

        Raises:
            AdapterError: If tool or version not found
        """
        if tool_name not in self.versions:
            raise AdapterError(f"Tool {tool_name} not found")

        if version not in self.versions[tool_name]:
            raise AdapterError(f"Version {version} not found for tool {tool_name}")

        return self.versions[tool_name][version]

    def list_versions(self, tool_name: str) -> list[VersionInfo]:
        """List all versions for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            list[VersionInfo]: List of version information

        Raises:
            AdapterError: If tool not found
        """
        if tool_name not in self.versions:
            raise AdapterError(f"Tool {tool_name} not found")

        return list(self.versions[tool_name].values())

    def deprecate_version(self, tool_name: str, version: str) -> None:
        """Mark a version as deprecated.

        Args:
            tool_name: Name of the tool
            version: Version string

        Raises:
            AdapterError: If tool or version not found
        """
        if tool_name not in self.versions:
            raise AdapterError(f"Tool {tool_name} not found")

        if version not in self.versions[tool_name]:
            raise AdapterError(f"Version {version} not found for tool {tool_name}")

        self.versions[tool_name][version].is_deprecated = True

    def _validate_version(self, version: str) -> None:
        """Validate a version string according to the strategy.

        Args:
            version: Version string to validate

        Raises:
            AdapterError: If version is invalid
        """
        if self.strategy == VersionStrategy.SEMANTIC:
            # Basic semantic version validation (x.y.z)
            parts = version.split(".")
            if len(parts) != 3 or not all(p.isdigit() for p in parts):
                raise AdapterError(
                    f"Invalid semantic version: {version}. Must be in format x.y.z"
                )
        elif self.strategy == VersionStrategy.DATE:
            # Basic date validation (YYYYMMDD)
            if len(version) != 8 or not version.isdigit():
                raise AdapterError(
                    f"Invalid date version: {version}. Must be in format YYYYMMDD"
                )
        elif self.strategy == VersionStrategy.INCREMENT:
            # Simple integer validation
            if not version.isdigit():
                raise AdapterError(
                    f"Invalid increment version: {version}. Must be a number"
                )
