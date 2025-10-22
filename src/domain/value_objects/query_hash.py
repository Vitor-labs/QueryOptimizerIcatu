"""Query hash value object.

This module defines the QueryHash value object used to uniquely identify
SQL queries combined with their target database type. Hashes are used for
caching, deduplication, and metadata lookups.
"""

import re
from hashlib import sha256

from domain.exceptions.domain_exceptions import InvalidQueryHashError
from domain.value_objects.database_type import DatabaseType


class QueryHash:
    """Immutable value object representing a unique query identifier.

    A query hash is a 16-character hexadecimal string derived from the
    combination of SQL query text and target database type. This ensures
    the same query optimized for different databases has different hashes.

    Attributes:
        value: The 16-character hexadecimal hash string

    Examples:
        >>> hash1 = QueryHash.from_query("SELECT * FROM users", DatabaseType.ORACLE)
        >>> hash2 = QueryHash.from_query("SELECT * FROM users", DatabaseType.SQLITE)
        >>> hash1 != hash2  # Different database types
        True
    """

    _HASH_LENGTH = 16
    _HASH_PATTERN = re.compile(r"^[a-f0-9]{16}$")

    def __init__(self, value: str) -> None:
        """Initialize QueryHash with validation.

        Args:
            value: 16-character hexadecimal hash string

        Raises:
            InvalidQueryHashError: If hash format is invalid
        """
        self._value = self._validate_hash(value)

    @classmethod
    def _validate_hash(cls, value: str) -> str:
        """Validate hash format.

        Args:
            value: Hash string to validate

        Returns:
            Validated hash string

        Raises:
            InvalidQueryHashError: If hash is invalid
        """
        if not value:
            raise InvalidQueryHashError("Query hash cannot be empty")

        if len(value) != cls._HASH_LENGTH:
            raise InvalidQueryHashError(
                f"Query hash must be {cls._HASH_LENGTH} characters, got {len(value)}"
            )

        if not cls._HASH_PATTERN.match(value):
            raise InvalidQueryHashError(
                f"Query hash must be hexadecimal lowercase, got: {value}"
            )
        return value

    @classmethod
    def from_query(cls, query: str, database_type: DatabaseType) -> "QueryHash":
        """Generate hash from SQL query and database type.

        The hash is deterministic: same query + database type always produces
        the same hash. Different database types produce different hashes for
        the same query to allow database-specific optimizations.

        Args:
            query: SQL query text
            database_type: Target database type

        Returns:
            Generated QueryHash instance

        Raises:
            ValueError: If query is empty or whitespace-only

        Examples:
            >>> hash_obj = QueryHash.from_query(
            ...     "SELECT id, name FROM users WHERE active = 1",
            ...     DatabaseType.ORACLE
            ... )
            >>> len(hash_obj.value)
            16
        """
        if not query or not query.strip():
            raise ValueError("Cannot generate hash from empty query")

        # Normalize query: strip whitespace and lowercase for consistent hashing
        # Combine database type and query for hash input
        # Generate SHA-256 and take first 16 characters
        return cls(
            sha256(
                f"{database_type.value}:{query.strip()}".encode("utf-8")
            ).hexdigest()[: cls._HASH_LENGTH]
        )

    @property
    def value(self) -> str:
        """Get the hash value.

        Returns:
            16-character hexadecimal hash string
        """
        return self._value

    def __str__(self) -> str:
        """String representation of the hash.

        Returns:
            Hash value as string
        """
        return self._value

    def __repr__(self) -> str:
        """Developer-friendly representation.

        Returns:
            String showing class name and hash value
        """
        return f"QueryHash('{self._value}')"

    def __eq__(self, other: object) -> bool:
        """Check equality with another QueryHash.

        Args:
            other: Object to compare with

        Returns:
            True if both are QueryHash instances with same value
        """
        if not isinstance(other, QueryHash):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        """Get hash code for use in sets and dicts.

        Returns:
            Hash code based on value
        """
        return hash(self._value)
