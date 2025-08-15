# src/infrastructure/db_conn.py
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

import cx_Oracle  # Oracle database connector

from config.logger import logger
from core.interfaces import DatabaseConnection
from core.types import DatabaseType


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection implementation."""

    def __init__(self, database_path: Path) -> None:
        """Initialize SQLite connection."""
        self._database_path = database_path
        self._connection: sqlite3.Connection | None = None

    async def connect(self) -> None:
        """Establish SQLite connection."""
        try:
            if not self._database_path.exists():
                raise FileNotFoundError(
                    f"SQLite database not found: {self._database_path}"
                )

            self._connection = sqlite3.connect(str(self._database_path))
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to SQLite database: {self._database_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """Close SQLite connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("SQLite connection closed")

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if not self._connection:
            raise RuntimeError("Database not connected")

        try:
            cursor = self._connection.cursor()
            cursor.execute(query)

            # Handle different query types
            if query.strip().upper().startswith(("SELECT", "WITH", "PRAGMA")):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self._connection.commit()
                return [{"rows_affected": cursor.rowcount}]

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    async def measure_query_performance(self, query: str, iterations: int = 3) -> float:
        """Measure query execution time in milliseconds."""
        if not self._connection:
            raise RuntimeError("Database not connected")

        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                await self.execute_query(query)
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # Convert to ms
            except Exception as e:
                logger.warning(f"Query failed during performance test: {str(e)}")
                times.append(float("inf"))  # Mark as failed

        # Return average time, excluding failed attempts
        valid_times = [t for t in times if t != float("inf")]
        return sum(valid_times) / len(valid_times) if valid_times else float("inf")

    def get_database_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.SQLITE


class OracleConnection(DatabaseConnection):
    """Oracle database connection implementation."""

    def __init__(self, connection_string: str) -> None:
        """Initialize Oracle connection."""
        self._connection_string = connection_string
        self._connection: cx_Oracle.Connection | None = None

    async def connect(self) -> None:
        """Establish Oracle connection."""
        try:
            self._connection = cx_Oracle.connect(self._connection_string)
            logger.info("Connected to Oracle database")
        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """Close Oracle connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Oracle connection closed")

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if not self._connection:
            raise RuntimeError("Database not connected")

        try:
            cursor = self._connection.cursor()
            cursor.execute(query)

            # Handle different query types
            if query.strip().upper().startswith(("SELECT", "WITH")):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                self._connection.commit()
                return [{"rows_affected": cursor.rowcount}]

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    async def measure_query_performance(self, query: str, iterations: int = 3) -> float:
        """Measure query execution time in milliseconds."""
        if not self._connection:
            raise RuntimeError("Database not connected")

        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                await self.execute_query(query)
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # Convert to ms
            except Exception as e:
                logger.warning(f"Query failed during performance test: {str(e)}")
                times.append(float("inf"))  # Mark as failed

        # Return average time, excluding failed attempts
        valid_times = [t for t in times if t != float("inf")]
        return sum(valid_times) / len(valid_times) if valid_times else float("inf")

    def get_database_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.ORACLE


class DatabaseConnectionFactory:
    """Factory for creating database connections."""

    @staticmethod
    def create_connection(
        database_type: DatabaseType, connection_params: Dict[str, Any]
    ) -> DatabaseConnection:
        """Create a database connection based on type and parameters."""
        if database_type == DatabaseType.SQLITE:
            database_path = Path(
                connection_params.get("database_path", "./database.db")
            )
            return SQLiteConnection(database_path)
        elif database_type == DatabaseType.ORACLE:
            connection_string = connection_params.get("connection_string")
            if not connection_string:
                raise ValueError("Oracle connection_string is required")
            return OracleConnection(connection_string)
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
