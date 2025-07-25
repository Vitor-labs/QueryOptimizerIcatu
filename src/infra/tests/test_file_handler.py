# tests/test_file_handler.py
import json
from pathlib import Path

import pytest

from infra.file_handler import LocalFileHandler


class TestLocalFileHandler:
    """Test LocalFileHandler functionality."""

    @pytest.fixture
    def file_handler(self) -> LocalFileHandler:
        """Create file handler instance."""
        return LocalFileHandler()

    @pytest.mark.asyncio
    async def test_read_sql_file_success(
        self, file_handler: LocalFileHandler, temp_sql_file: Path
    ):
        """Test successful SQL file reading."""
        assert (
            await file_handler.read_sql_file(temp_sql_file)
        ) == "SELECT * FROM users WHERE age > 18;"

    @pytest.mark.asyncio
    async def test_read_sql_file_not_found(
        self, file_handler: LocalFileHandler, tmp_path: Path
    ):
        """Test reading non-existent SQL file."""
        with pytest.raises(FileNotFoundError):
            await file_handler.read_sql_file(tmp_path / "missing.sql")

    @pytest.mark.asyncio
    async def test_read_sql_file_wrong_extension(
        self, file_handler: LocalFileHandler, tmp_path: Path
    ):
        """Test reading file with wrong extension."""
        wrong_file = tmp_path / "test.txt"
        wrong_file.write_text("some content")
        with pytest.raises(ValueError, match="Expected .sql file"):
            await file_handler.read_sql_file(wrong_file)

    @pytest.mark.asyncio
    async def test_write_json_file_success(
        self, file_handler: LocalFileHandler, temp_json_file: Path
    ):
        """Test successful JSON file writing."""
        test_data = {"key": "value", "number": 42}
        await file_handler.write_json_file(temp_json_file, test_data)

        assert temp_json_file.exists()
        assert json.loads(temp_json_file.read_text()) == test_data
