"""Port (interface) for prompt generation.

This port defines the contract for generating database-specific prompts
used in the SQL optimization process.
"""

from abc import ABC, abstractmethod

from domain.value_objects.database_type import DatabaseType


class PromptGeneratorPort(ABC):
    """Abstract interface for database-specific prompt generation.

    This port enables the application layer to generate prompts without
    coupling to specific prompt templates or generation strategies.

    Examples:
        >>> generator = get_prompt_generator(DatabaseType.ORACLE)
        >>> prompt = generator.sql_to_natural("SELECT * FROM users")
    """

    @abstractmethod
    def sql_to_natural(self, query: str) -> str:
        """Generate prompt for converting SQL to natural language.

        Args:
            query: SQL query to explain

        Returns:
            Formatted prompt for LLM

        Examples:
            >>> generator = get_prompt_generator(DatabaseType.ORACLE)
            >>> prompt = generator.sql_to_natural("SELECT * FROM users WHERE age > 18")
            >>> # Use prompt with LLM to get explanation
        """

    @abstractmethod
    def natural_to_sql(self, explanation: str) -> str:
        """Generate prompt for converting natural language to SQL.

        Args:
            explanation: Natural language description of what the query should do

        Returns:
            Formatted prompt for LLM

        Examples:
            >>> generator = get_prompt_generator(DatabaseType.ORACLE)
            >>> prompt = generator.natural_to_sql("Get all active users older than 18")
            >>> # Use prompt with LLM to get optimized SQL
        """

    @abstractmethod
    def get_database_type(self) -> DatabaseType:
        """Get the database type this generator supports.

        Returns:
            Database type enum value

        Examples:
            >>> generator = get_prompt_generator(DatabaseType.ORACLE)
            >>> generator.get_database_type()
            DatabaseType.ORACLE
        """

    def validate_query(self, query: str) -> bool:
        """Validate that a query is appropriate for this database type.

        This is an optional method that can be overridden to provide
        database-specific query validation.

        Args:
            query: SQL query to validate

        Returns:
            True if query appears valid for this database type

        Examples:
            >>> generator = get_prompt_generator(DatabaseType.ORACLE)
            >>> is_valid = generator.validate_query("SELECT * FROM users")
        """
        # Basic validation: not empty and contains SELECT/INSERT/UPDATE/DELETE
        if not query or not query.strip():
            return False

        return any(
            query.strip().upper().startswith(keyword)
            for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH", "CREATE"]
        )
