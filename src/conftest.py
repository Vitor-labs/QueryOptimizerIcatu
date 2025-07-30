# tests/conftest.py
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from core.types import DatabaseType, QueryMetadata


@pytest.fixture
def sample_sql_query() -> str:
    """Sample SQL query for testing."""
    return "SELECT * FROM users WHERE age > 18;"


@pytest.fixture
def sample_metadata() -> QueryMetadata:
    """Sample metadata for testing."""
    return QueryMetadata(
        query_sql="SELECT * FROM users WHERE age > 18;",
        explanation_text="This query selects all users older than 18",
        version="1.0",
        last_optimization=datetime.now(),
        database_type=DatabaseType.ORACLE,
    )


@pytest.fixture
def mock_llm_client() -> Mock:
    """Mock LLM client for testing."""
    client = Mock()
    client.generate_response = AsyncMock(return_value="Generated response")
    client.get_provider_name.return_value = "test"
    return client


@pytest.fixture
def temp_sql_file(tmp_path: Path) -> Path:
    """Create temporary SQL file for testing."""
    sql_file = tmp_path / "test_query.sql"
    sql_file.write_text("SELECT * FROM users WHERE age > 18;")
    return sql_file


@pytest.fixture
def temp_json_file(tmp_path: Path) -> Path:
    """Create temporary JSON file path for testing."""
    return tmp_path / "test_metadata.json"
