"""Factory for creating database-specific prompt generators."""

from application.ports.prompt_port import PromptGeneratorPort
from domain.value_objects.database_type import DatabaseType
from infrastructure.prompts.mysql_generator import MySQLPromptGenerator
from infrastructure.prompts.oracle_generator import OraclePromptGenerator
from infrastructure.prompts.postgresql_generator import PostgreSQLPromptGenerator
from infrastructure.prompts.sqlite_generator import SQLitePromptGenerator
from infrastructure.prompts.sqlserver_generator import SQLServerPromptGenerator


class PromptGeneratorFactory:
	"""Factory for creating database-specific prompt generators.

	This factory creates the appropriate prompt generator based on
	the target database type, encapsulating the creation logic.

	Examples:
		>>> generator = PromptGeneratorFactory.create(DatabaseType.ORACLE)
		>>> prompt = generator.sql_to_natural("SELECT * FROM users")
	"""

	_generators: dict[DatabaseType, type[PromptGeneratorPort]] = {
		DatabaseType.ORACLE: OraclePromptGenerator,
		DatabaseType.SQLITE: SQLitePromptGenerator,
		DatabaseType.SQLSERVER: SQLServerPromptGenerator,
		DatabaseType.POSTGRESQL: PostgreSQLPromptGenerator,
		DatabaseType.MYSQL: MySQLPromptGenerator,
	}

	@classmethod
	def create(cls, database_type: DatabaseType) -> PromptGeneratorPort:
		"""Create prompt generator for database type.

		Args:
			database_type: Target database type

		Returns:
			Configured prompt generator instance

		Raises:
			ValueError: If database type is not supported

		Examples:
			>>> oracle_gen = PromptGeneratorFactory.create(DatabaseType.ORACLE)
			>>> sqlite_gen = PromptGeneratorFactory.create(DatabaseType.SQLITE)
		"""
		if generator_class := cls._generators.get(database_type):
			return generator_class()

		raise ValueError(
			f"Unsupported database type: {database_type}. "
			f"Supported types: {', '.join(t.value for t in cls._generators.keys())}"
		)

	@classmethod
	def supported_databases(cls) -> list[DatabaseType]:
		"""Get list of supported database types.

		Returns:
			List of DatabaseType enums that have generators
		"""
		return list(cls._generators.keys())
