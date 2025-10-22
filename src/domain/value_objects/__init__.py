"""Value objects for the domain layer.

Value objects are immutable objects defined by their attributes rather than identity.
They represent descriptive aspects of the domain with no conceptual identity.
"""

from domain.value_objects.database_type import DatabaseType
from domain.value_objects.query_hash import QueryHash

__all__ = ["DatabaseType", "QueryHash"]
