"""Data Transfer Objects for optimization results.

DTOs are used to transfer data across architectural boundaries without
exposing internal domain entities. They provide a stable API contract.
"""

from dataclasses import dataclass
from datetime import datetime

from domain.entities.optimization import OptimizationResult
from domain.value_objects.database_type import DatabaseType


@dataclass(frozen=True)
class OptimizationDTO:
    """DTO for transferring optimization results across boundaries.

    This immutable DTO represents the public API for optimization results,
    decoupling external consumers from internal domain entities.

    Attributes:
        query_hash: Unique identifier for the query
        original_query: Original SQL query text
        explanation: Natural language explanation of the query
        optimized_query: Optimized SQL query text
        database_type: Target database system
        version: Optimization version number
        optimized_at: When optimization was performed

    Examples:
        >>> dto = OptimizationDTO(
        ...     query_hash="abc123def456",
        ...     original_query="SELECT * FROM users",
        ...     explanation="Get all users",
        ...     optimized_query="SELECT u.* FROM users u",
        ...     database_type="oracle",
        ...     version="1.0",
        ...     optimized_at=datetime.now()
        ... )
    """

    query_hash: str
    original_query: str
    explanation: str
    optimized_query: str
    database_type: str
    version: str
    optimized_at: datetime

    @classmethod
    def from_result(cls, result: OptimizationResult) -> "OptimizationDTO":
        """Create DTO from domain entity.

        Args:
            result: Domain optimization result entity

        Returns:
            DTO representation of the result

        Examples:
            >>> result = OptimizationResult(metadata=..., optimized_query=...)
            >>> dto = OptimizationDTO.from_result(result)
            >>> dto.database_type
            'oracle'
        """
        return cls(
            query_hash=result.query_hash.value,
            original_query=result.original_query,
            explanation=result.explanation,
            optimized_query=result.optimized_query,
            database_type=result.database_type.value,
            version=result.version,
            optimized_at=result.metadata.optimized_at,
        )

    def to_dict(self) -> dict[str, str]:
        """Convert DTO to dictionary for serialization.

        Returns:
            Dictionary with all fields as primitive types

        Examples:
            >>> dto = OptimizationDTO(...)
            >>> data = dto.to_dict()
            >>> data['database_type']
            'oracle'
        """
        return {
            "query_hash": self.query_hash,
            "original_query": self.original_query,
            "explanation": self.explanation,
            "optimized_query": self.optimized_query,
            "database_type": self.database_type,
            "version": self.version,
            "optimized_at": self.optimized_at.isoformat(),
        }


@dataclass(frozen=True)
class ComparisonDTO:
    """DTO for comparing optimizations across multiple databases.

    This DTO aggregates optimization results for the same query
    optimized for different database systems.

    Attributes:
        original_query: The original SQL query
        optimizations: Map of database type to optimization result

    Examples:
        >>> comparison = ComparisonDTO(
        ...     original_query="SELECT * FROM users",
        ...     optimizations={
        ...         "oracle": oracle_dto,
        ...         "sqlite": sqlite_dto,
        ...     }
        ... )
    """

    original_query: str
    optimizations: dict[str, OptimizationDTO]

    def get_optimization(self, database_type: DatabaseType) -> OptimizationDTO | None:
        """Get optimization result for specific database type.

        Args:
            database_type: Database type to retrieve

        Returns:
            Optimization DTO if available, None otherwise

        Examples:
            >>> comparison = ComparisonDTO(...)
            >>> oracle_result = comparison.get_optimization(DatabaseType.ORACLE)
        """
        return self.optimizations.get(database_type.value)

    def database_types(self) -> list[str]:
        """Get list of database types included in comparison.

        Returns:
            List of database type strings

        Examples:
            >>> comparison = ComparisonDTO(...)
            >>> comparison.database_types()
            ['oracle', 'sqlite', 'sqlserver']
        """
        return list(self.optimizations.keys())

    def to_dict(self) -> dict[str, str | dict]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "original_query": self.original_query,
            "optimizations": {
                db_type: opt.to_dict() for db_type, opt in self.optimizations.items()
            },
        }
