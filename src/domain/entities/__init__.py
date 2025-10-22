"""Domain entities for SQL query optimization.

Entities are objects with identity that are defined by their lifecycle and attributes.
They encapsulate business logic and maintain invariants.
"""

from domain.entities.optimization import OptimizationMetadata, OptimizationResult

__all__ = ["OptimizationMetadata", "OptimizationResult"]
