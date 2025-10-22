"""SQLite database prompt generator."""

from domain.value_objects.database_type import DatabaseType
from infrastructure.prompts.base_generator import BasePromptGenerator


class SQLitePromptGenerator(BasePromptGenerator):
	"""Prompt generator for SQLite.

	Generates prompts optimized for SQLite's lightweight nature and
	specific features like WITHOUT ROWID, partial indexes, and built-in functions.

	Examples:
		>>> generator = SQLitePromptGenerator()
		>>> prompt = generator.natural_to_sql("Get all users created last month")
	"""

	def get_database_name(self) -> str:
		"""Get database name.

		Returns:
			"SQLite"
		"""
		return "SQLite"

	def get_specific_features(self) -> str:
		"""Get SQLite-specific features to mention.

		Returns:
			Description of SQLite features
		"""
		return "- Built-in functions (SUBSTR, LENGTH, DATETIME)\n- WITHOUT ROWID tables\n- Partial indexes"

	def get_specific_requirements(self) -> str:
		"""Get SQLite-specific optimization requirements.

		Returns:
			Multi-line string of requirements
		"""
		return """Use SQLite built-in functions (SUBSTR, LENGTH, COALESCE, IFNULL, DATETIME)
Consider WITHOUT ROWID for tables with non-integer primary keys
Use partial indexes (CREATE INDEX ... WHERE ...) for filtered queries
Leverage Common Table Expressions (WITH clause)
Use window functions where appropriate (supported in SQLite 3.25+)
Consider PRAGMA directives for query optimization
Avoid features not supported by SQLite (e.g., RIGHT JOIN, FULL OUTER JOIN)
Use simple, efficient queries as SQLite has limited optimization"""

	def get_database_type(self) -> DatabaseType:
		"""Get database type enum.

		Returns:
			DatabaseType.SQLITE
		"""
		return DatabaseType.SQLITE
