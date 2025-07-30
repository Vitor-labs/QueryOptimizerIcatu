# src/core/types.py (updated)
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OptimizationStage(Enum):
    """Stages of the optimization process."""

    SQL_TO_NATURAL = "sql_to_natural"
    NATURAL_TO_SQL = "natural_to_sql"


class DatabaseType(Enum):
    """Supported database types."""

    ORACLE = "oracle"
    SQLITE = "sqlite"


@dataclass
class QueryMetadata:
    """Metadata for a SQL query optimization."""

    query_sql: str
    explanation_text: str
    version: str
    last_optimization: datetime
    database_type: DatabaseType

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {
            "query_sql": self.query_sql,
            "explanation_text": self.explanation_text,
            "version": self.version,
            "last_optimization": self.last_optimization.isoformat(),
            "database_type": self.database_type.value,
        }


@dataclass
class OptimizationResult:
    """Result of query optimization process."""

    original_query: str
    explained_query: str
    optimized_query: str
    metadata: QueryMetadata
    database_type: DatabaseType
