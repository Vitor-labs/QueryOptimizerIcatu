# src/infrastructure/file_handler.py
import json
from pathlib import Path
from typing import Any

from config.logger import logger
from core.interfaces import FileHandler


class LocalFileHandler(FileHandler):
    """Local file system handler implementation."""

    async def read_sql_file(self, file_path: Path) -> str:
        """Read SQL content from file."""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"SQL file not found: {file_path}")

            if file_path.suffix.lower() != ".sql":
                raise ValueError(f"Expected .sql file, got: {file_path.suffix}")

            if not (content := file_path.read_text(encoding="utf-8").strip()):
                raise ValueError(f"SQL file is empty: {file_path}")

            logger.info(f"Successfully read SQL file: {file_path}")
            return content

        except Exception as e:
            logger.error(f"Error reading SQL file {file_path}: {str(e)}")
            raise

    async def write_json_file(self, file_path: Path, data: dict[str, Any]) -> None:
        """Write JSON data to file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(  # Write JSON with pretty formatting
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info(f"Successfully wrote JSON file: {file_path}")

        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {str(e)}")
            raise
