"""Domain layer for SQL Query Optimizer.

The domain layer contains enterprise business rules and is the innermost layer
in Clean Architecture. It has no dependencies on outer layers and defines:

- Entities: Objects with identity and lifecycle
- Value Objects: Immutable objects defined by their attributes
- Domain Exceptions: Business rule violations

This layer should be:
- Framework-agnostic
- Database-agnostic
- UI-agnostic
- Testable in isolation
"""

from domain.entities.optimization import OptimizationMetadata, OptimizationResult
from domain.exceptions.domain_exceptions import (
    DomainError,
    InvalidDatabaseTypeError,
    InvalidQueryHashError,
    InvalidVersionError,
    LLMProviderError,
    MetadataNotFoundError,
    OptimizationError,
    QueryValidationError,
)
from domain.value_objects.database_type import DatabaseType
from domain.value_objects.query_hash import QueryHash

__all__ = [
    # Entities
    "OptimizationMetadata",
    "OptimizationResult",
    # Value Objects
    "DatabaseType",
    "QueryHash",
    # Exceptions
    "DomainError",
    "QueryValidationError",
    "LLMProviderError",
    "MetadataNotFoundError",
    "InvalidDatabaseTypeError",
    "InvalidQueryHashError",
    "InvalidVersionError",
    "OptimizationError",
]
