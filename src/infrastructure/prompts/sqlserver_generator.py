"""SQL Server database prompt generator."""

from domain.value_objects.database_type import DatabaseType
from infrastructure.prompts.base_generator import BasePromptGenerator


class SQLServerPromptGenerator(BasePromptGenerator):
	"""Prompt generator for Microsoft SQL Server.

	Generates prompts optimized for SQL Server's T-SQL syntax, table hints,
	and specific features like CROSS APPLY and indexed views.

	Examples:
		>>> generator = SQLServerPromptGenerator()
		>>> prompt = generator.sql_to_natural("SELECT * FROM users WITH (NOLOCK)")
	"""

	def get_database_name(self) -> str:
		"""Get database name.

		Returns:
			"SQL Server"
		"""
		return "SQL Server"

	def get_specific_features(self) -> str:
		"""Get SQL Server-specific features to mention.

		Returns:
			Description of SQL Server features
		"""
		return "- Table hints (WITH (NOLOCK), WITH (INDEX))\n- T-SQL functions\n- CROSS APPLY/OUTER APPLY"

	def get_specific_requirements(self) -> str:
		"""Get SQL Server-specific optimization requirements.

		Returns:
			Multi-line string of requirements
		"""
		return """Use T-SQL syntax compatible with Microsoft SQL Server
Consider table hints (WITH (NOLOCK), WITH (INDEX), WITH (FORCESEEK))
Leverage window functions and OVER clause
Use CROSS APPLY or OUTER APPLY for correlated operations
Consider SQL Server functions (ISNULL, TRY_CAST, DATEPART, FORMAT)
Use Common Table Expressions (WITH clause) for readability
Consider indexed views for complex aggregations
Use TOP or OFFSET-FETCH for pagination
Leverage SQL Server query optimizer hints when beneficial"""

	def get_database_type(self) -> DatabaseType:
		"""Get database type enum.

		Returns:
			DatabaseType.SQLSERVER
		"""
		return DatabaseType.SQLSERVER
