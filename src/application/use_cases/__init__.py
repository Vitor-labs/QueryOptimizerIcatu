"""Use cases for the application layer.

Use cases encapsulate application-specific business rules and orchestrate
the flow of data between entities and ports.
"""

from application.use_cases.compare_optimizations import CompareOptimizationsUseCase
from application.use_cases.optimize_query import OptimizeQueryUseCase

__all__ = ["OptimizeQueryUseCase", "CompareOptimizationsUseCase"]
