"""Prompt templates for SQL optimization.

This module provides reusable prompt templates that can be customized
for different database types.
"""

from string import Template


class PromptTemplates:
	"""Collection of prompt templates for SQL optimization.

	These templates use Python's string.Template for safe string substitution.
	Templates can be customized per database type while maintaining consistency.
	"""

	SQL_TO_NATURAL = Template("""
	You are an expert $database_name database analyst. Your task is to:
	explain the following SQL query in simple, natural language.

	$database_name SQL Query:
	```sql
	$query
	```
	Please provide a concise explanation of what this query does. Focus on:

	What data it retrieves or modifies
	Which tables/views are involved
	Key conditions and filters
	Any joins or complex operations
	$database_name-specific features used$specific_features
	Keep the explanation clear and minimal - avoid technical jargon where possible.

	Explanation:
	""")
	NATURAL_TO_SQL = Template("""
	You are an expert $database_name SQL developer.
	Based on the following natural language description, write an optimized SQL query.
	Description: $explanation

	Requirements:

	Write $database_name-specific SQL syntax
	Focus on performance optimization
	Use appropriate $database_name features and functions $specific_requirements
	Consider $database_name query optimizer behavior
	Provide ONLY the SQL query without additional explanation
	Optimized SQL Query:
	""")

	@classmethod
	def render_sql_to_natural(
		cls, database_name: str, query: str, specific_features: str = ""
	) -> str:
		"""Render SQL-to-natural language prompt.

		Args:
			database_name: Name of database system
			query: SQL query to explain
			specific_features: Additional database-specific features to mention

		Returns:
			Rendered prompt string
		"""
		return cls.SQL_TO_NATURAL.substitute(
			database_name=database_name,
			query=query,
			specific_features=f"\n{specific_features}" if specific_features else "",
		)

	@classmethod
	def render_natural_to_sql(
		cls, database_name: str, explanation: str, specific_requirements: str
	) -> str:
		"""Render natural-to-SQL prompt.

		Args:
			database_name: Name of database system
			explanation: Natural language description
			specific_requirements: Database-specific optimization requirements

		Returns:
			Rendered prompt string
		"""
		# Format requirements as bullet points
		return cls.NATURAL_TO_SQL.substitute(
			database_name=database_name,
			explanation=explanation,
			specific_requirements="\n".join(
				f"- {req}" for req in specific_requirements.split("\n") if req.strip()
			),
		)
