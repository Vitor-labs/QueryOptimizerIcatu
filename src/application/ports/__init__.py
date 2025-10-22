"""Application ports (interfaces) for dependency inversion.

Ports define contracts that infrastructure adapters must implement.
They enable the application layer to remain independent of external concerns.
"""

from application.ports.llm_port import LLMPort
from application.ports.prompt_port import PromptGeneratorPort
from application.ports.storage_port import FileStoragePort, MetadataRepositoryPort

__all__ = [
    "LLMPort",
    "FileStoragePort",
    "MetadataRepositoryPort",
    "PromptGeneratorPort",
]
