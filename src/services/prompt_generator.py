# src/services/prompt_generators.py
from core.interfaces import PromptGenerator
from core.types import DatabaseType


class OraclePromptGenerator(PromptGenerator):
    """Generates prompts for Oracle database optimization."""

    def generate_sql_to_natural_prompt(self, sql_query: str) -> str:
        """Generate prompt for Oracle SQL to natural language conversion."""
        return f"""
        You are an expert Oracle database analyst. Your task is to explain the following Oracle SQL query in simple, natural language.

        Oracle SQL Query:
        ```sql
        {sql_query}
        Please provide a concise explanation of what this query does. Focus on:

        What data it retrieves or modifies
        Which tables/views are involved
        Key conditions and filters
        Any joins or complex operations
        Oracle-specific features used (hints, functions, etc.)
        Keep the explanation clear and minimal - avoid technical jargon where possible.

        Explanation: """

    def generate_natural_to_sql_prompt(self, explanation: str) -> str:
        """Generate prompt for natural language to Oracle SQL conversion."""
        return f"""
        You are an expert Oracle SQL developer. Based on the following natural language description, write an optimized Oracle SQL query.

        Description: {explanation}

        Requirements:

        Write Oracle-specific SQL syntax
        Focus on performance optimization
        Use appropriate Oracle hints if beneficial (/*+ HINT */)
        Consider proper indexing strategies in your query structure
        Use modern Oracle SQL features where appropriate (analytical functions, CTEs, etc.)
        Use Oracle-specific functions when beneficial (NVL, DECODE, ROWNUM, etc.)
        Consider Oracle optimizer behavior
        Please provide only the SQL query without additional explanation: """

    def get_database_type(self) -> DatabaseType:
        """Get the database type this generator supports."""
        return DatabaseType.ORACLE


class SQLitePromptGenerator(PromptGenerator):
    """Generates prompts for SQLite database optimization."""

    def generate_sql_to_natural_prompt(self, sql_query: str) -> str:
        """Generate prompt for SQLite SQL to natural language conversion."""
        return f"""
        You are an expert SQLite database analyst. Your task is to explain the following SQLite SQL query in simple, natural language.

        SQLite SQL Query:

        sql

        {sql_query}
        Please provide a concise explanation of what this query does. Focus on:

        What data it retrieves or modifies
        Which tables/views are involved
        Key conditions and filters
        Any joins or complex operations
        SQLite-specific features used (PRAGMA, built-in functions, etc.)
        Keep the explanation clear and minimal - avoid technical jargon where possible.

        Explanation: """

    def generate_natural_to_sql_prompt(self, explanation: str) -> str:
        """Generate prompt for natural language to SQLite SQL conversion."""
        return f"""
        You are an expert SQLite SQL developer. Based on the following natural language description, write an optimized SQLite SQL query.

        Description: {explanation}

        Requirements:

        Write SQLite-specific SQL syntax
        Focus on performance optimization for SQLite
        Use SQLite built-in functions where appropriate (SUBSTR, LENGTH, COALESCE, etc.)
        Consider SQLite indexing strategies
        Use SQLite-specific features (WITHOUT ROWID, partial indexes, etc.)
        Use Common Table Expressions (CTEs) and window functions where beneficial
        Consider SQLite query planner behavior
        Avoid features not supported by SQLite
        Please provide only the SQL query without additional explanation: """

    def get_database_type(self) -> DatabaseType:
        """Get the database type this generator supports."""
        return DatabaseType.SQLITE


class PromptGeneratorFactory:
    """Factory for creating database-specific prompt generators."""

    @staticmethod
    def create_generator(database_type: DatabaseType) -> PromptGenerator:
        """Create a prompt generator for the specified database type."""
        if database_type == DatabaseType.ORACLE:
            return OraclePromptGenerator()
        elif database_type == DatabaseType.SQLITE:
            return SQLitePromptGenerator()
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
