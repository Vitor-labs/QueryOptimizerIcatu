"""MySQL database prompt generator."""

from domain.value_objects.database_type import DatabaseType
from infrastructure.prompts.base_generator import BasePromptGenerator


class MySQLPromptGenerator(BasePromptGenerator):
	"""Prompt generator for MySQL.

	Generates prompts optimized for MySQL's specific syntax and features
	including optimizer hints, JSON functions, and storage engine considerations.

	Examples:
		>>> generator = MySQLPromptGenerator()
		>>> prompt = generator.natural_to_sql("Find users with most recent orders")
	"""

	def get_database_name(self) -> str:
		"""Get database name.

		Returns:
			"MySQL"
		"""
		return "MySQL"

	def get_specific_features(self) -> str:
		"""Get MySQL-specific features to mention.

		Returns:
			Description of MySQL features
		"""
		return "- Optimizer hints\n- JSON functions\n- Index hints (USE INDEX, FORCE INDEX)"

	def get_specific_requirements(self) -> str:
		"""Get MySQL-specific optimization requirements.

		Returns:
			Multi-line string of requirements
		"""
		return """Use MySQL-specific syntax (MySQL 8.0+)
Consider optimizer hints (/*+ HINT */) when beneficial
Use JSON functions (JSON_EXTRACT, JSON_CONTAINS, ->, ->>)
Leverage index hints (USE INDEX, FORCE INDEX) when needed
Use Common Table Expressions (WITH clause) in MySQL 8.0+
Consider window functions (MySQL 8.0+)
Use MySQL functions (IFNULL, COALESCE, CONCAT, DATE_FORMAT)
Consider storage engine implications (InnoDB optimizations)
Use LIMIT for pagination efficiently"""

	def get_database_type(self) -> DatabaseType:
		"""Get database type enum.

		Returns:
			DatabaseType.MYSQL
		"""
		return DatabaseType.MYSQL
