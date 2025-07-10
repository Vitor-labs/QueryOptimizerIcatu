# src/infrastructure/metadata_repository.py
import hashlib
import json
from datetime import datetime
from pathlib import Path

from config.logger import logger
from core.interfaces import MetadataRepository
from core.types import QueryMetadata


class JsonMetadataRepository(MetadataRepository):
    """JSON-based metadata repository implementation."""

    def __init__(
        self, storage_path: Path = Path("./optimization_metadata.json")
    ) -> None:
        """Initialize with storage path."""
        self._storage_path = storage_path
        self._metadata_cache: dict[str, QueryMetadata] = {}
        self._load_metadata()

    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for SQL query."""
        return hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]

    def _load_metadata(self) -> None:
        """Load metadata from storage."""
        try:
            if self._storage_path.exists():
                for query_hash, metadata_dict in json.loads(
                    self._storage_path.read_text(encoding="utf-8")
                ).items():
                    self._metadata_cache[query_hash] = QueryMetadata(
                        query_sql=metadata_dict["query_sql"],
                        explanation_text=metadata_dict["explanation_text"],
                        version=metadata_dict["version"],
                        last_optimization=datetime.fromisoformat(
                            metadata_dict["last_optimization"]
                        ),
                    )
                logger.info(f"Loaded {len(self._metadata_cache)} metadata entries")
        except Exception as e:
            logger.warning(f"Could not load metadata: {str(e)}")
            self._metadata_cache = {}

    def _save_metadata(self) -> None:
        """Save metadata to storage."""
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._storage_path.write_text(
                json.dumps(
                    {
                        query_hash: metadata.to_dict()
                        for query_hash, metadata in self._metadata_cache.items()
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            logger.info("Metadata saved successfully")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            raise

    def generate_hash_for_query(self, query: str) -> str:
        """Generate hash for a SQL query (public method)."""
        return self._generate_query_hash(query)

    async def get_metadata(self, query_hash: str) -> QueryMetadata | None:
        """Retrieve metadata for a query."""
        return self._metadata_cache.get(query_hash)

    async def save_metadata(self, query_hash: str, metadata: QueryMetadata) -> None:
        """Save metadata for a query."""
        self._metadata_cache[query_hash] = metadata
        self._save_metadata()
