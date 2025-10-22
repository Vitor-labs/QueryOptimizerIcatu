"""Optimization entities for the domain layer.

This module contains the core domain entities representing SQL query optimizations,
their metadata, and results. These entities encapsulate business logic and rules.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from domain.exceptions.domain_exceptions import (
    InvalidVersionError,
    QueryValidationError,
)
from domain.value_objects.database_type import DatabaseType
from domain.value_objects.query_hash import QueryHash


@dataclass
class OptimizationMetadata:
    """Metadata for a SQL query optimization.

    This entity represents the metadata associated with an optimization attempt,
    including versioning, timestamps, and the optimization content itself.

    Attributes:
        query_hash: Unique identifier for the query + database combination
        original_query: The original SQL query text
        explanation: Natural language explanation of the query
        database_type: Target database system
        version: Semantic version string (e.g., "1.0", "1.1")
        optimized_at: Timestamp when optimization was performed

    Examples:
        >>> metadata = OptimizationMetadata(
        ...     query_hash=QueryHash.from_query("SELECT * FROM users", DatabaseType.ORACLE),
        ...     original_query="SELECT * FROM users",
        ...     explanation="Retrieve all users from the users table",
        ...     database_type=DatabaseType.ORACLE,
        ... )
        >>> metadata.increment_version()
        >>> metadata.version
        '1.1'
    """

    query_hash: QueryHash
    original_query: str
    explanation: str
    database_type: DatabaseType
    version: str = "1.0"
    optimized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    _VERSION_PATTERN = re.compile(r"^\d+\.\d+$")

    def __post_init__(self) -> None:
        """Validate metadata after initialization.

        Raises:
            QueryValidationError: If original_query is empty
            InvalidVersionError: If version format is invalid
        """
        if not self.original_query or not self.original_query.strip():
            raise QueryValidationError("Original query cannot be empty")

        if not self._VERSION_PATTERN.match(self.version):
            raise InvalidVersionError(
                f"Version must be in format 'major.minor', got: {self.version}"
            )
        if self.optimized_at.tzinfo is None:  # Ensure timezone-aware datetime
            object.__setattr__(
                self, "optimized_at", self.optimized_at.replace(tzinfo=timezone.utc)
            )

    def increment_version(self) -> None:
        """Increment the minor version number.

        Increments the second number in the version string (e.g., "1.0" -> "1.1").
        This is called when an optimization is re-run on the same query.

        Examples:
            >>> metadata = OptimizationMetadata(...)
            >>> metadata.version = "1.0"
            >>> metadata.increment_version()
            >>> metadata.version
            '1.1'
            >>> metadata.increment_version()
            >>> metadata.version
            '1.2'
        """
        major, minor = self.version.split(".")
        self.version = f"{major}.{int(minor) + 1}"
        self.optimized_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, str | int]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary with all metadata fields as primitive types

        Examples:
            >>> metadata = OptimizationMetadata(...)
            >>> data = metadata.to_dict()
            >>> isinstance(data, dict)
            True
            >>> 'query_hash' in data
            True
        """
        return {
            "query_hash": self.query_hash.value,
            "original_query": self.original_query,
            "explanation": self.explanation,
            "database_type": self.database_type.value,
            "version": self.version,
            "optimized_at": self.optimized_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "OptimizationMetadata":
        """Create OptimizationMetadata from dictionary.

        Args:
            data: Dictionary containing metadata fields

        Returns:
            New OptimizationMetadata instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If field values are invalid

        Examples:
            >>> data = {
            ...     "query_hash": "abc123def456",
            ...     "original_query": "SELECT * FROM users",
            ...     "explanation": "Get all users",
            ...     "database_type": "oracle",
            ...     "version": "1.0",
            ...     "optimized_at": "2024-01-01T12:00:00+00:00",
            ... }
            >>> metadata = OptimizationMetadata.from_dict(data)
            >>> metadata.version
            '1.0'
        """
        return cls(
            query_hash=QueryHash(data["query_hash"]),
            original_query=data["original_query"],
            explanation=data["explanation"],
            database_type=DatabaseType.from_string(data["database_type"]),
            version=data.get("version", "1.0"),
            optimized_at=datetime.fromisoformat(data["optimized_at"]),
        )

    @classmethod
    def create_new(
        cls, query: str, database_type: DatabaseType, explanation: str = ""
    ) -> "OptimizationMetadata":
        """Factory method to create new metadata for a query.

        Args:
            query: SQL query text
            database_type: Target database type
            explanation: Optional initial explanation

        Returns:
            New OptimizationMetadata instance with version "1.0"

        Examples:
            >>> metadata = OptimizationMetadata.create_new(
            ...     "SELECT * FROM users",
            ...     DatabaseType.ORACLE
            ... )
            >>> metadata.version
            '1.0'
        """
        return cls(
            query_hash=QueryHash.from_query(query, database_type),
            original_query=query,
            explanation=explanation,
            database_type=database_type,
            version="1.0",
            optimized_at=datetime.now(timezone.utc),
        )


@dataclass(frozen=True)
class OptimizationResult:
    """Result of a SQL query optimization process.

    This immutable entity represents the complete result of optimizing a query,
    including the original query, explanation, optimized version, and metadata.

    Attributes:
        metadata: Optimization metadata including versioning and timestamps
        optimized_query: The optimized SQL query text

    Examples:
        >>> result = OptimizationResult(
        ...     metadata=metadata,
        ...     optimized_query="SELECT u.* FROM users u WHERE u.active = 1"
        ... )
        >>> result.database_type
        DatabaseType.ORACLE
    """

    metadata: OptimizationMetadata
    optimized_query: str

    def __post_init__(self) -> None:
        """Validate result after initialization.

        Raises:
            QueryValidationError: If optimized_query is empty
        """
        if not self.optimized_query or not self.optimized_query.strip():
            raise QueryValidationError("Optimized query cannot be empty")

    @property
    def original_query(self) -> str:
        """Get the original SQL query.

        Returns:
            Original query text from metadata
        """
        return self.metadata.original_query

    @property
    def explanation(self) -> str:
        """Get the natural language explanation.

        Returns:
            Query explanation from metadata
        """
        return self.metadata.explanation

    @property
    def database_type(self) -> DatabaseType:
        """Get the target database type.

        Returns:
            Database type from metadata
        """
        return self.metadata.database_type

    @property
    def query_hash(self) -> QueryHash:
        """Get the query hash.

        Returns:
            Query hash from metadata
        """
        return self.metadata.query_hash

    @property
    def version(self) -> str:
        """Get the optimization version.

        Returns:
            Version string from metadata
        """
        return self.metadata.version

    def to_dict(self) -> dict[str, str | int]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary with all result fields

        Examples:
            >>> result = OptimizationResult(...)
            >>> data = result.to_dict()
            >>> 'optimized_query' in data
            True
        """
        return {**self.metadata.to_dict(), "optimized_query": self.optimized_query}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "OptimizationResult":
        """Create OptimizationResult from dictionary.

        Args:
            data: Dictionary containing result fields

        Returns:
            New OptimizationResult instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If field values are invalid
        """
        return cls(
            metadata=OptimizationMetadata.from_dict(data),
            optimized_query=data["optimized_query"],
        )

    def with_updated_explanation(self, explanation: str) -> "OptimizationResult":
        """Create new result with updated explanation.

        Since OptimizationResult is immutable, this creates a new instance.

        Args:
            explanation: New explanation text

        Returns:
            New OptimizationResult with updated explanation
        """
        return OptimizationResult(
            metadata=OptimizationMetadata(
                query_hash=self.metadata.query_hash,
                original_query=self.metadata.original_query,
                explanation=explanation,
                database_type=self.metadata.database_type,
                version=self.metadata.version,
                optimized_at=self.metadata.optimized_at,
            ),
            optimized_query=self.optimized_query,
        )
