"""Ports (interfaces) for storage operations.

This module defines contracts for file storage and metadata persistence,
allowing the application layer to work with different storage backends.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from domain.entities.optimization import OptimizationMetadata
from domain.value_objects.database_type import DatabaseType
from domain.value_objects.query_hash import QueryHash


class FileStoragePort(ABC):
    """Abstract interface for file storage operations.

    This port enables reading SQL files and writing JSON results without
    coupling to specific file system implementations.

    Examples:
        >>> storage = get_file_storage()
        >>> content = await storage.read_text(Path("query.sql"))
        >>> await storage.write_json(Path("result.json"), {"key": "value"})
    """

    @abstractmethod
    async def read_text(self, path: Path) -> str:
        """Read text content from a file.

        Args:
            path: Path to the file to read

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read due to permissions
            ValueError: If file is empty or invalid

        Examples:
            >>> storage = get_file_storage()
            >>> sql = await storage.read_text(Path("query.sql"))
            >>> print(sql)
            SELECT * FROM users;
        """

    @abstractmethod
    async def write_json(
        self, path: Path, data: dict[str, str | int | float | bool | None]
    ) -> None:
        """Write data to a JSON file.

        Args:
            path: Path where JSON file should be written
            data: Dictionary to serialize as JSON

        Raises:
            PermissionError: If file cannot be written due to permissions
            ValueError: If data cannot be serialized to JSON

        Examples:
            >>> storage = get_file_storage()
            >>> await storage.write_json(
            ...     Path("result.json"),
            ...     {"status": "success", "version": "1.0"}
            ... )
        """

    @abstractmethod
    async def exists(self, path: Path) -> bool:
        """Check if a file exists.

        Args:
            path: Path to check

        Returns:
            True if file exists, False otherwise

        Examples:
            >>> storage = get_file_storage()
            >>> if await storage.exists(Path("query.sql")):
            ...     print("File found")
        """


class MetadataRepositoryPort(ABC):
    """Abstract interface for optimization metadata persistence.

    This port defines operations for storing and retrieving optimization metadata,
    abstracting the underlying storage mechanism (JSON, database, etc.).

    Examples:
        >>> repo = get_metadata_repository()
        >>> metadata = await repo.get(query_hash)
        >>> await repo.save(metadata)
    """

    @abstractmethod
    async def get(self, query_hash: QueryHash) -> OptimizationMetadata | None:
        """Retrieve optimization metadata by query hash.

        Args:
            query_hash: Unique identifier for the query

        Returns:
            OptimizationMetadata if found, None otherwise

        Examples:
            >>> repo = get_metadata_repository()
            >>> metadata = await repo.get(QueryHash("abc123def456"))
            >>> if metadata:
            ...     print(f"Version: {metadata.version}")
        """

    @abstractmethod
    async def save(self, metadata: OptimizationMetadata) -> None:
        """Save or update optimization metadata.

        If metadata with the same query hash exists, it will be updated.
        Otherwise, a new entry is created.

        Args:
            metadata: Metadata to persist

        Raises:
            PermissionError: If storage cannot be written
            ValueError: If metadata is invalid

        Examples:
            >>> repo = get_metadata_repository()
            >>> await repo.save(metadata)
        """

    @abstractmethod
    async def delete(self, query_hash: QueryHash) -> bool:
        """Delete optimization metadata.

        Args:
            query_hash: Hash of metadata to delete

        Returns:
            True if metadata was deleted, False if it didn't exist

        Examples:
            >>> repo = get_metadata_repository()
            >>> was_deleted = await repo.delete(query_hash)
        """

    @abstractmethod
    async def list_all(self) -> list[OptimizationMetadata]:
        """List all stored optimization metadata.

        Returns:
            List of all metadata entries

        Examples:
            >>> repo = get_metadata_repository()
            >>> all_metadata = await repo.list_all()
            >>> for meta in all_metadata:
            ...     print(f"{meta.query_hash}: {meta.version}")
        """

    @abstractmethod
    async def find_by_database_type(
        self, database_type: DatabaseType
    ) -> list[OptimizationMetadata]:
        """Find all metadata for a specific database type.

        Args:
            database_type: Database type to filter by

        Returns:
            List of metadata entries for the specified database type

        Examples:
            >>> repo = get_metadata_repository()
            >>> oracle_metadata = await repo.find_by_database_type(DatabaseType.ORACLE)
        """
