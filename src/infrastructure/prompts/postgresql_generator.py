"""PostgreSQL database prompt generator."""

from domain.value_objects.database_type import DatabaseType
from infrastructure.prompts.base_generator import BasePromptGenerator


class PostgreSQLPromptGenerator(BasePromptGenerator):
	"""Prompt generator for PostgreSQL.

	Generates prompts optimized for PostgreSQL's advanced features including
	JSON/JSONB operations, array functions, and advanced indexing.

	Examples:
		>>> generator = PostgreSQLPromptGenerator()
		>>> prompt = generator.sql_to_natural("SELECT data->>'name' FROM users")
	"""

	def get_database_name(self) -> str:
		"""Get database name.

		Returns:
			"PostgreSQL"
		"""
		return "PostgreSQL"

	def get_specific_features(self) -> str:
		"""Get PostgreSQL-specific features to mention.

		Returns:
			Description of PostgreSQL features
		"""
		return "- JSON/JSONB operators\n- Array functions\n- Advanced indexing (GIN, GiST, BRIN)"

	def get_specific_requirements(self) -> str:
		"""Get PostgreSQL-specific optimization requirements.

		Returns:
			Multi-line string of requirements
		"""
		return """Use PostgreSQL-specific syntax and features
Leverage JSONB operators (->, ->>, @>, etc.) for JSON data
Use array functions and operators where appropriate
Consider advanced index types (GIN for JSON/arrays, GiST for ranges)
Use Common Table Expressions (WITH clause) and LATERAL joins
Leverage window functions and advanced aggregates
Use PostgreSQL functions (COALESCE, NULLIF, GREATEST, LEAST)
Consider materialized views for complex queries
Use EXPLAIN ANALYZE output to guide optimizations"""

	def get_database_type(self) -> DatabaseType:
		"""Get database type enum.

		Returns:
			DatabaseType.POSTGRESQL
		"""
		return DatabaseType.POSTGRESQL
