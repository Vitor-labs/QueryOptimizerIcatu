"""Data Transfer Objects for the application layer.

DTOs provide a stable API contract and decouple external interfaces
from internal domain entities.
"""

from application.dto.optimization_dto import ComparisonDTO, OptimizationDTO

__all__ = ["OptimizationDTO", "ComparisonDTO"]
