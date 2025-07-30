# tests/test_query_optimizer.py
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from config.config import OptimizerConfig
from core.types import DatabaseType
from services.query_optimizer import DatabaseQueryOptimizer


class TestDatabaseQueryOptimizer:
    """Test DatabaseQueryOptimizer functionality."""

    @pytest.fixture
    def optimizer_config(self) -> OptimizerConfig:
        """Create optimizer configuration."""
        return OptimizerConfig(provider="gemini", database_type=DatabaseType.ORACLE)

    @pytest.fixture
    def optimizer(self, mock_llm_client, optimizer_config) -> DatabaseQueryOptimizer:
        """Create optimizer instance with mocks."""
        file_handler = Mock()
        file_handler.read_sql_file = AsyncMock(return_value="SELECT * FROM users;")
        file_handler.write_json_file = AsyncMock()

        metadata_repo = Mock()
        metadata_repo.get_metadata = AsyncMock(return_value=None)
        metadata_repo.save_metadata = AsyncMock()

        return DatabaseQueryOptimizer(
            llm_client=mock_llm_client,
            file_handler=file_handler,
            metadata_repo=metadata_repo,
            config=optimizer_config,
            database_type=DatabaseType.ORACLE,
        )

    @pytest.mark.asyncio
    async def test_optimize_query_success(
        self, optimizer: DatabaseQueryOptimizer, temp_sql_file: Path
    ):
        """Test successful query optimization."""
        # Configure mock responses
        optimizer._llm_client.generate_response.side_effect = [
            "This query selects all users from the users table",  # SQL to natural
            "SELECT u.* FROM users u ORDER BY u.id;",  # Natural to SQL
        ]
        result = await optimizer.optimize_query(temp_sql_file)

        assert result.original_query == "SELECT * FROM users;"
        assert "selects all users" in result.explained_query
        assert "SELECT u.*" in result.optimized_query
        assert result.database_type == DatabaseType.ORACLE

        # Verify calls were made
        assert optimizer._llm_client.generate_response.call_count == 2
        optimizer._file_handler.read_sql_file.assert_called_once_with(temp_sql_file)
        optimizer._metadata_repo.save_metadata.assert_called_once()

    @pytest.mark.asyncio
    async def test_optimize_query_file_error(
        self, optimizer: DatabaseQueryOptimizer, temp_sql_file: Path
    ):
        """Test optimization with file reading error."""
        optimizer._file_handler.read_sql_file.side_effect = FileNotFoundError(
            "File not found"
        )
        with pytest.raises(FileNotFoundError):
            await optimizer.optimize_query(temp_sql_file)
