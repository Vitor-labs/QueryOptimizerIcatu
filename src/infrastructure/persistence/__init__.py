"""Persistence adapters for file storage and metadata.

This module provides concrete implementations of storage ports
for the infrastructure layer.
"""

from infrastructure.persistence.file_handler import LocalFileHandler, SyncFileHandler
from infrastructure.persistence.metadata_repository import (
    InMemoryMetadataRepository,
    JsonMetadataRepository,
)

__all__ = [
    "LocalFileHandler",
    "SyncFileHandler",
    "JsonMetadataRepository",
    "InMemoryMetadataRepository",
]
