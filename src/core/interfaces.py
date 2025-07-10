# src/core/interfaces.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from core.types import OptimizationResult, QueryMetadata


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate_response(self, prompt: str, config: dict[str, Any]) -> str:
        """Generate response from the LLM."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name for this client."""
        pass


class FileHandler(ABC):
    """Abstract interface for file operations."""

    @abstractmethod
    async def read_sql_file(self, file_path: Path) -> str:
        """Read SQL content from file."""
        pass

    @abstractmethod
    async def write_json_file(self, file_path: Path, data: dict[str, Any]) -> None:
        """Write JSON data to file."""
        pass


class MetadataRepository(ABC):
    """Abstract interface for metadata persistence."""

    @abstractmethod
    async def get_metadata(self, query_hash: str) -> QueryMetadata | None:
        """Retrieve metadata for a query."""
        pass

    @abstractmethod
    async def save_metadata(self, query_hash: str, metadata: QueryMetadata) -> None:
        """Save metadata for a query."""
        pass


class QueryOptimizer(ABC):
    """Abstract interface for query optimization."""

    @abstractmethod
    async def optimize_query(self, sql_file_path: Path) -> OptimizationResult:
        """Optimize a SQL query from file."""
        pass
