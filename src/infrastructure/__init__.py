"""Infrastructure layer for SQL Query Optimizer.

The infrastructure layer contains implementations of interfaces defined
in the application layer. It handles external concerns like:

- LLM provider integrations (Gemini, OpenAI, Claude, Oracle GenAI)
- File system operations
- Data persistence
- Configuration management
- Logging

This layer depends on the application and domain layers but is independent
of the presentation layer.
"""

from infrastructure.config.logger import get_logger
from infrastructure.config.settings import Settings
from infrastructure.llm.factory import LLMAdapterFactory
from infrastructure.persistence.file_handler import LocalFileHandler
from infrastructure.persistence.metadata_repository import JsonMetadataRepository
from infrastructure.prompts.factory import PromptGeneratorFactory

__all__ = [
	# Configuration
	"Settings",
	"get_logger",
	# Factories
	"LLMAdapterFactory",
	"PromptGeneratorFactory",
	# Implementations
	"LocalFileHandler",
	"JsonMetadataRepository",
]
