"""Oracle database prompt generator."""

from domain.value_objects.database_type import DatabaseType
from infrastructure.prompts.base_generator import BasePromptGenerator


class OraclePromptGenerator(BasePromptGenerator):
	"""Prompt generator for Oracle Database.

	Generates prompts optimized for Oracle-specific features including
	hints, analytic functions, hierarchical queries, and optimizer behavior.

	Examples:
		>>> generator = OraclePromptGenerator()
		>>> prompt = generator.sql_to_natural("SELECT /*+ FULL(t) */ * FROM table t")
	"""

	def get_database_name(self) -> str:
		"""Get database name.

		Returns:
			"Oracle"
		"""
		return "Oracle"

	def get_specific_features(self) -> str:
		"""Get Oracle-specific features to mention.

		Returns:
			Description of Oracle features
		"""
		return "- Oracle hints (/*+ HINT */)\n- Analytic functions\n- Hierarchical queries (CONNECT BY)"

	def get_specific_requirements(self) -> str:
		"""Get Oracle-specific optimization requirements.

		Returns:
			Multi-line string of requirements
		"""
		return """Use Oracle hints (/*+ HINT */) when beneficial for performance
Leverage analytic/window functions (ROW_NUMBER, RANK, LAG, LEAD)
Use Common Table Expressions (WITH clause) for complex queries
Consider Oracle-specific functions (NVL, NVL2, DECODE, COALESCE)
Use ROWNUM or ROW_NUMBER() for pagination
Consider materialized views for complex aggregations
Use proper join methods (NESTED LOOPS, HASH JOIN, MERGE JOIN)
Leverage Oracle's Cost-Based Optimizer (CBO) behavior"""

	def get_database_type(self) -> DatabaseType:
		"""Get database type enum.

		Returns:
			DatabaseType.ORACLE
		"""
		return DatabaseType.ORACLE
