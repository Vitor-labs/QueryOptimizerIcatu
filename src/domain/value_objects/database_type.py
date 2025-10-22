"""Database type value object.

This module defines the DatabaseType enum representing supported database systems.
Each database type has specific SQL dialects, optimization strategies, and features.
"""

from enum import Enum


class DatabaseType(Enum):
    """Enumeration of supported database systems.

    Each value represents a different SQL dialect and optimization strategy.
    The value string is used for serialization and user-facing displays.

    Attributes:
        ORACLE: Oracle Database (11g+)
        SQLITE: SQLite (3.x)
        SQLSERVER: Microsoft SQL Server (2016+)
        POSTGRESQL: PostgreSQL (12+)
        MYSQL: MySQL (8.0+)
    """

    ORACLE = "oracle"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

    @classmethod
    def from_string(cls, value: str) -> "DatabaseType":
        """Create DatabaseType from string value.

        Args:
            value: Database type string (case-insensitive)

        Returns:
            DatabaseType enum member

        Raises:
            ValueError: If value doesn't match any database type

        Examples:
            >>> DatabaseType.from_string("oracle")
            DatabaseType.ORACLE
            >>> DatabaseType.from_string("SQLITE")
            DatabaseType.SQLITE
        """
        try:
            return cls(value.lower())
        except ValueError as e:
            valid_types = ", ".join(t.value for t in cls)
            raise ValueError(
                f"Invalid database type: '{value}'. Valid types: {valid_types}"
            ) from e

    @property
    def display_name(self) -> str:
        """Get human-readable database name.

        Returns:
            Properly capitalized database name

        Examples:
            >>> DatabaseType.ORACLE.display_name
            'Oracle'
            >>> DatabaseType.SQLSERVER.display_name
            'SQL Server'
        """
        display_names = {
            DatabaseType.ORACLE: "Oracle",
            DatabaseType.SQLITE: "SQLite",
            DatabaseType.SQLSERVER: "SQL Server",
            DatabaseType.POSTGRESQL: "PostgreSQL",
            DatabaseType.MYSQL: "MySQL",
        }
        return display_names[self]

    def supports_hints(self) -> bool:
        """Check if database supports query hints/optimizer directives.

        Returns:
            True if database supports hints, False otherwise

        Examples:
            >>> DatabaseType.ORACLE.supports_hints()
            True
            >>> DatabaseType.SQLITE.supports_hints()
            False
        """
        return self in {DatabaseType.ORACLE, DatabaseType.SQLSERVER}

    def supports_cte(self) -> bool:
        """Check if database supports Common Table Expressions (WITH clause).

        Returns:
            True if CTEs are supported, False otherwise
        """
        # All modern databases support CTEs
        return True

    def supports_window_functions(self) -> bool:
        """Check if database supports window functions.

        Returns:
            True if window functions are supported, False otherwise
        """
        # All supported database versions have window functions
        return True

    def max_identifier_length(self) -> int:
        """Get maximum length for table/column identifiers.

        Returns:
            Maximum number of characters allowed in identifiers
        """
        max_lengths = {
            DatabaseType.ORACLE: 128,  # Oracle 12.2+
            DatabaseType.SQLITE: 1000,  # Practical limit
            DatabaseType.SQLSERVER: 128,
            DatabaseType.POSTGRESQL: 63,
            DatabaseType.MYSQL: 64,
        }
        return max_lengths[self]
