"""Application layer for SQL Query Optimizer.

The application layer contains application-specific business rules and orchestrates
the flow of data between the domain layer and outer layers. It defines:

- Use Cases: Application-specific business logic
- Ports (Interfaces): Contracts for external dependencies
- DTOs: Data transfer objects for crossing boundaries

This layer:
- Depends only on the domain layer
- Defines interfaces that infrastructure implements
- Orchestrates domain entities
- Remains independent of frameworks and UI
"""

from application.dto.optimization_dto import ComparisonDTO, OptimizationDTO
from application.ports.llm_port import LLMPort
from application.ports.prompt_port import PromptGeneratorPort
from application.ports.storage_port import FileStoragePort, MetadataRepositoryPort
from application.use_cases.compare_optimizations import CompareOptimizationsUseCase
from application.use_cases.optimize_query import OptimizeQueryUseCase

__all__ = [
    # Use Cases
    "OptimizeQueryUseCase",
    "CompareOptimizationsUseCase",
    # Ports
    "LLMPort",
    "FileStoragePort",
    "MetadataRepositoryPort",
    "PromptGeneratorPort",
    # DTOs
    "OptimizationDTO",
    "ComparisonDTO",
]
