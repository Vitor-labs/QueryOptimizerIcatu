"""Domain-specific exceptions for the SQL Query Optimizer.

This module defines all domain-layer exceptions following the fail-fast principle.
All exceptions inherit from DomainError for easy catching at application boundaries.
"""


class DomainError(Exception):
    """Base class for all domain-layer errors.

    This exception should never be raised directly. Use specific subclasses instead.
    Application layer should catch this to handle all domain errors uniformly.
    """


class QueryValidationError(DomainError):
    """Raised when SQL query validation fails.

    Examples:
        - Empty query string
        - Invalid SQL syntax
        - Query exceeds maximum length
    """


class LLMProviderError(DomainError):
    """Raised when LLM provider encounters an error.

    Examples:
        - API rate limit exceeded
        - Invalid API response
        - Network timeout
        - Authentication failure
    """


class MetadataNotFoundError(DomainError):
    """Raised when requested metadata cannot be found.

    This indicates a metadata entry doesn't exist in the repository,
    which may be expected behavior in some cases.
    """


class InvalidDatabaseTypeError(DomainError):
    """Raised when an invalid or unsupported database type is specified.

    Examples:
        - Unknown database type string
        - Database type not in supported list
    """


class InvalidQueryHashError(DomainError):
    """Raised when a query hash is malformed or invalid.

    Examples:
        - Hash length is incorrect
        - Hash contains invalid characters
        - Empty hash value
    """


class InvalidVersionError(DomainError):
    """Raised when version string is malformed.

    Examples:
        - Version doesn't follow semver pattern
        - Negative version numbers
        - Invalid version format
    """


class OptimizationError(DomainError):
    """Raised when query optimization process fails.

    This is a general error for optimization failures that don't
    fit into more specific error categories.
    """
