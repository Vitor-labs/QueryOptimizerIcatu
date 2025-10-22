"""Base prompt generator with common functionality.

This module provides a base class for database-specific prompt generators,
reducing code duplication and ensuring consistency.
"""

from abc import ABC, abstractmethod

from application.ports.prompt_port import PromptGeneratorPort
from infrastructure.prompts.templates import PromptTemplates


class BasePromptGenerator(PromptGeneratorPort, ABC):
	"""Base class for database-specific prompt generators.

	This class provides common functionality and template rendering,
	allowing subclasses to focus on database-specific requirements.

	Subclasses must implement:
	- get_database_name()
	- get_specific_requirements()
	- get_database_type()
	"""

	@abstractmethod
	def get_database_name(self) -> str:
		"""Get human-readable database name.

		Returns:
			Database name for prompts (e.g., "Oracle", "SQLite")
		"""

	@abstractmethod
	def get_specific_requirements(self) -> str:
		"""Get database-specific optimization requirements.

		Returns:
			Multi-line string of requirements, one per line
		"""

	def get_specific_features(self) -> str:
		"""Get database-specific features to mention in explanations.

		This is optional and can be overridden by subclasses.

		Returns:
			Description of specific features (empty string if none)
		"""
		return ""

	def sql_to_natural(self, query: str) -> str:
		"""Generate SQL-to-natural language prompt.

		Args:
			query: SQL query to explain

		Returns:
			Formatted prompt for LLM
		"""
		return PromptTemplates.render_sql_to_natural(
			database_name=self.get_database_name(),
			query=query,
			specific_features=self.get_specific_features(),
		)

	def natural_to_sql(self, explanation: str) -> str:
		"""Generate natural-to-SQL prompt.

		Args:
			explanation: Natural language description

		Returns:
			Formatted prompt for LLM
		"""
		return PromptTemplates.render_natural_to_sql(
			database_name=self.get_database_name(),
			explanation=explanation,
			specific_requirements=self.get_specific_requirements(),
		)
