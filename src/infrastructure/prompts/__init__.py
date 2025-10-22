"""Prompt generators for database-specific SQL optimization.

This module provides prompt generation implementations for various
database systems, encapsulating database-specific optimization knowledge.
"""

from infrastructure.prompts.factory import PromptGeneratorFactory
from infrastructure.prompts.mysql_generator import MySQLPromptGenerator
from infrastructure.prompts.oracle_generator import OraclePromptGenerator
from infrastructure.prompts.postgresql_generator import PostgreSQLPromptGenerator
from infrastructure.prompts.sqlite_generator import SQLitePromptGenerator
from infrastructure.prompts.sqlserver_generator import SQLServerPromptGenerator

__all__ = [
	"OraclePromptGenerator",
	"SQLitePromptGenerator",
	"SQLServerPromptGenerator",
	"PostgreSQLPromptGenerator",
	"MySQLPromptGenerator",
	"PromptGeneratorFactory",
]
