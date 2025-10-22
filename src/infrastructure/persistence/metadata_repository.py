"""Metadata repository implementation using JSON storage.

This module provides persistence for optimization metadata using
a JSON file as the storage backend.
"""

import json
from pathlib import Path

import aiofiles

from application.ports.storage_port import MetadataRepositoryPort
from domain.entities.optimization import OptimizationMetadata
from domain.value_objects.database_type import DatabaseType
from domain.value_objects.query_hash import QueryHash
from infrastructure.config.logger import get_logger

logger = get_logger(__name__)


class JsonMetadataRepository(MetadataRepositoryPort):
    """JSON file-based metadata repository implementation.

    This repository stores optimization metadata in a JSON file with
    in-memory caching for performance. All operations are async-safe.

    Attributes:
        _storage_path: Path to JSON storage file
        _cache: In-memory cache of metadata entries

    Examples:
        >>> repo = JsonMetadataRepository(Path("metadata.json"))
        >>> await repo.save(metadata)
        >>> retrieved = await repo.get(query_hash)
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize metadata repository.

        Args:
            storage_path: Path to JSON storage file (defaults to ./optimization_metadata.json)
        """
        self._storage_path = storage_path or Path("./optimization_metadata.json")
        self._cache: dict[str, OptimizationMetadata] = {}
        self._initialized = False

        logger.info(
            "Metadata repository initialized", storage_path=str(self._storage_path)
        )

    async def _ensure_initialized(self) -> None:
        """Ensure repository is initialized by loading existing data.

        This is called lazily on first access to avoid I/O during construction.
        """
        if not self._initialized:
            await self._load_metadata()
            self._initialized = True

    async def _load_metadata(self) -> None:
        """Load metadata from storage file into cache."""
        if not self._storage_path.exists():
            logger.info("No existing metadata file found, starting fresh")
            self._cache = {}
            return

        try:
            async with aiofiles.open(self._storage_path, "r", encoding="utf-8") as f:
                content = await f.read()

            data = json.loads(content)

            # Parse each metadata entry
            for hash_str, metadata_dict in data.items():
                try:
                    self._cache[hash_str] = OptimizationMetadata.from_dict(
                        metadata_dict
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to load metadata entry",
                        hash=hash_str,
                        error=str(e),
                    )

            logger.info(
                "Metadata loaded from storage",
                entries=len(self._cache),
                path=str(self._storage_path),
            )

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in metadata file", error=str(e))
            self._cache = {}
        except Exception as e:
            logger.error("Failed to load metadata", error=str(e))
            self._cache = {}

    async def _save_metadata(self) -> None:
        """Save metadata cache to storage file."""
        try:
            # Ensure parent directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert cache to serializable dict
            data = {
                hash_str: metadata.to_dict()
                for hash_str, metadata in self._cache.items()
            }

            # Write to file
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            async with aiofiles.open(self._storage_path, "w", encoding="utf-8") as f:
                await f.write(json_content)

            logger.debug(
                "Metadata saved to storage",
                entries=len(self._cache),
                path=str(self._storage_path),
            )

        except Exception as e:
            logger.error("Failed to save metadata", error=str(e))
            raise

    async def get(self, query_hash: QueryHash) -> OptimizationMetadata | None:
        """Retrieve optimization metadata by query hash.

        Args:
            query_hash: Unique identifier for the query

        Returns:
            OptimizationMetadata if found, None otherwise
        """
        await self._ensure_initialized()

        result = self._cache.get(query_hash.value)

        if result:
            logger.debug("Metadata cache hit", query_hash=query_hash.value)
        else:
            logger.debug("Metadata cache miss", query_hash=query_hash.value)

        return result

    async def save(self, metadata: OptimizationMetadata) -> None:
        """Save or update optimization metadata.

        Args:
            metadata: Metadata to persist
        """
        await self._ensure_initialized()

        hash_value = metadata.query_hash.value
        is_new = hash_value not in self._cache

        self._cache[hash_value] = metadata
        await self._save_metadata()

        logger.info(
            "Metadata saved",
            query_hash=hash_value,
            version=metadata.version,
            is_new=is_new,
        )

    async def delete(self, query_hash: QueryHash) -> bool:
        """Delete optimization metadata.

        Args:
            query_hash: Hash of metadata to delete

        Returns:
            True if metadata was deleted, False if it didn't exist
        """
        await self._ensure_initialized()

        if query_hash.value in self._cache:
            del self._cache[query_hash.value]
            await self._save_metadata()

            logger.info("Metadata deleted", query_hash=query_hash.value)
            return True

        logger.debug("Metadata not found for deletion", query_hash=query_hash.value)
        return False

    async def list_all(self) -> list[OptimizationMetadata]:
        """List all stored optimization metadata.

        Returns:
            List of all metadata entries
        """
        await self._ensure_initialized()
        return list(self._cache.values())

    async def find_by_database_type(
        self,
        database_type: DatabaseType,
    ) -> list[OptimizationMetadata]:
        """Find all metadata for a specific database type.

        Args:
            database_type: Database type to filter by

        Returns:
            List of metadata entries for the specified database type
        """
        await self._ensure_initialized()

        return [
            metadata
            for metadata in self._cache.values()
            if metadata.database_type == database_type
        ]


class InMemoryMetadataRepository(MetadataRepositoryPort):
    """In-memory metadata repository for testing.

    This repository stores metadata in memory only, useful for testing
    or scenarios where persistence is not needed.

    Examples:
        >>> repo = InMemoryMetadataRepository()
        >>> await repo.save(metadata)
    """

    def __init__(self) -> None:
        """Initialize in-memory repository."""
        self._storage: dict[str, OptimizationMetadata] = {}

    async def get(self, query_hash: QueryHash) -> OptimizationMetadata | None:
        """Retrieve metadata by query hash."""
        return self._storage.get(query_hash.value)

    async def save(self, metadata: OptimizationMetadata) -> None:
        """Save metadata."""
        self._storage[metadata.query_hash.value] = metadata

    async def delete(self, query_hash: QueryHash) -> bool:
        """Delete metadata."""
        if query_hash.value in self._storage:
            del self._storage[query_hash.value]
            return True
        return False

    async def list_all(self) -> list[OptimizationMetadata]:
        """List all metadata."""
        return list(self._storage.values())

    async def find_by_database_type(
        self,
        database_type: DatabaseType,
    ) -> list[OptimizationMetadata]:
        """Find metadata by database type."""
        return [
            metadata
            for metadata in self._storage.values()
            if metadata.database_type == database_type
        ]
