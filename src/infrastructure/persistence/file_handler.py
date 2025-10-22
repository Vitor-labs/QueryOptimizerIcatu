"""File storage adapter implementation.

This module provides concrete implementation of file storage operations
using async file I/O for better performance.
"""

import json
from pathlib import Path

import aiofiles

from application.ports.storage_port import FileStoragePort
from infrastructure.config.logger import get_logger

logger = get_logger(__name__)


class LocalFileHandler(FileStoragePort):
    """Local file system storage implementation using async I/O.

    This adapter provides asynchronous file operations for reading SQL files
    and writing JSON results, implementing the FileStoragePort interface.

    Examples:
        >>> handler = LocalFileHandler()
        >>> sql = await handler.read_text(Path("query.sql"))
        >>> await handler.write_json(Path("result.json"), {"key": "value"})
    """

    async def read_text(self, path: Path) -> str:
        """Read text content from a file asynchronously.

        Args:
            path: Path to the file to read

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read due to permissions
            ValueError: If file is empty
        """
        logger.debug("Reading file", path=str(path))

        if not path.exists():  # Validate file exists
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():  # Validate it's a file
            raise ValueError(f"Path is not a file: {path}")

        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()

            if not content.strip():  # Validate content is not empty
                raise ValueError(f"File is empty: {path}")

            logger.info("File read successfully", path=str(path), size=len(content))
            return content.strip()

        except FileNotFoundError:
            raise
        except PermissionError as e:
            logger.error("Permission denied reading file", path=str(path))
            raise PermissionError(f"Cannot read file {path}: {e}") from e
        except Exception as e:
            logger.error("Error reading file", path=str(path), error=str(e))
            raise ValueError(f"Error reading file {path}: {e}") from e

    async def write_json(
        self,
        path: Path,
        data: dict[str, str | int | float | bool | None],
    ) -> None:
        """Write data to a JSON file asynchronously.

        Args:
            path: Path where JSON file should be written
            data: Dictionary to serialize as JSON

        Raises:
            PermissionError: If file cannot be written due to permissions
            ValueError: If data cannot be serialized to JSON
        """
        logger.debug("Writing JSON file", path=str(path))

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Serialize to JSON with pretty formatting
            json_content = json.dumps(data, indent=2, ensure_ascii=False)

            # Write asynchronously
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json_content)

            logger.info(
                "JSON file written successfully", path=str(path), size=len(json_content)
            )

        except PermissionError as e:
            logger.error("Permission denied writing file", path=str(path))
            raise PermissionError(f"Cannot write file {path}: {e}") from e
        except (TypeError, ValueError) as e:
            logger.error("JSON serialization failed", path=str(path), error=str(e))
            raise ValueError(f"Cannot serialize data to JSON: {e}") from e
        except Exception as e:
            logger.error("Error writing file", path=str(path), error=str(e))
            raise ValueError(f"Error writing file {path}: {e}") from e

    async def exists(self, path: Path) -> bool:
        """Check if a file exists.

        Args:
            path: Path to check

        Returns:
            True if file exists and is a regular file, False otherwise
        """
        return path.exists() and path.is_file()


class SyncFileHandler(FileStoragePort):
    """Synchronous file system storage implementation.

    This is a simpler synchronous version for environments where
    async I/O is not needed or available.

    Examples:
        >>> handler = SyncFileHandler()
        >>> sql = await handler.read_text(Path("query.sql"))
    """

    async def read_text(self, path: Path) -> str:
        """Read text content from a file synchronously.

        Args:
            path: Path to the file to read

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid
        """
        logger.debug("Reading file (sync)", path=str(path))

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        try:
            content = path.read_text(encoding="utf-8")

            if not content.strip():
                raise ValueError(f"File is empty: {path}")

            logger.info("File read successfully", path=str(path), size=len(content))
            return content.strip()

        except Exception as e:
            logger.error("Error reading file", path=str(path), error=str(e))
            raise ValueError(f"Error reading file {path}: {e}") from e

    async def write_json(
        self,
        path: Path,
        data: dict[str, str | int | float | bool | None],
    ) -> None:
        """Write data to a JSON file synchronously.

        Args:
            path: Path where JSON file should be written
            data: Dictionary to serialize as JSON

        Raises:
            PermissionError: If file cannot be written
            ValueError: If data cannot be serialized
        """
        logger.debug("Writing JSON file (sync)", path=str(path))

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            path.write_text(json_content, encoding="utf-8")

            logger.info("JSON file written successfully", path=str(path))

        except Exception as e:
            logger.error("Error writing file", path=str(path), error=str(e))
            raise ValueError(f"Error writing file {path}: {e}") from e

    async def exists(self, path: Path) -> bool:
        """Check if a file exists.

        Args:
            path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return path.exists() and path.is_file()
