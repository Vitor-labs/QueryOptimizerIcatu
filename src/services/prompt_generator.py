# src/services/prompt_generator.py


class PromptGenerator:
    """Generates prompts for different optimization stages."""

    @staticmethod
    def generate_sql_to_natural_prompt(sql_query: str) -> str:
        """Generate prompt for SQL to natural language conversion."""
        return f"""
        You are an expert Oracle database analyst. Your task is to explain the following SQL query in simple, natural language.

        SQL Query:
        ```sql
        {sql_query}
        Please provide a concise explanation of what this query does. Focus on:

        What data it retrieves or modifies
        Which tables/views are involved
        Key conditions and filters
        Any joins or complex operations
        Keep the explanation clear and minimal - avoid technical jargon where possible.

        Explanation:"""

    @staticmethod
    def generate_natural_to_sql_prompt(explanation: str) -> str:
        """Generate prompt for natural language to SQL conversion."""
        return f"""
        You are an expert Oracle SQL developer. Based on the following natural language description, write an optimized Oracle SQL query.

        Description: {explanation}

        Requirements:

        Write Oracle-specific SQL syntax
        Focus on performance optimization
        Use appropriate Oracle hints if beneficial
        Consider proper indexing strategies in your query structure
        Use modern Oracle SQL features where appropriate
        Please provide only the SQL query without additional explanation: """
