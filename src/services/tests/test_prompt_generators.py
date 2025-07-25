# tests/test_prompt_generators.py

from core.types import DatabaseType
from services.prompt_generator import OraclePromptGenerator, SQLitePromptGenerator


class TestPromptGenerators:
    """Test prompt generator functionality."""

    def test_oracle_prompt_generator(self):
        """Test Oracle prompt generator."""
        generator = OraclePromptGenerator()

        assert generator.get_database_type() == DatabaseType.ORACLE

        sql_query = "SELECT * FROM users WHERE age > 18;"
        sql_prompt = generator.generate_sql_to_natural_prompt(sql_query)

        assert "Oracle" in sql_prompt
        assert sql_query in sql_prompt
        assert "Oracle-specific features" in sql_prompt

    def test_sqlite_prompt_generator(self):
        """Test SQLite prompt generator."""
        generator = SQLitePromptGenerator()

        assert generator.get_database_type() == DatabaseType.SQLITE

        explanation = "Get all users older than 18"
        natural_prompt = generator.generate_natural_to_sql_prompt(explanation)

        assert "SQLite" in natural_prompt
        assert explanation in natural_prompt
        assert "SQLite-specific" in natural_prompt
