# src/services/query_validator.py
import hashlib
from typing import Any, Dict, List

from config.logger import logger
from core.interfaces import DatabaseConnection, QueryValidator


class DatabaseQueryValidator(QueryValidator):
    """Database query validator implementation."""

    async def validate_queries_equivalent(
        self,
        original_query: str,
        optimized_query: str,
        db_connection: DatabaseConnection,
    ) -> bool:
        """Validate that two queries produce equivalent results."""
        try:
            logger.info("Validating query equivalence...")

            # Execute both queries
            original_results = await db_connection.execute_query(original_query)
            optimized_results = await db_connection.execute_query(optimized_query)

            # For non-SELECT queries, just check if both executed successfully
            if not (
                original_query.strip().upper().startswith(("SELECT", "WITH"))
                and optimized_query.strip().upper().startswith(("SELECT", "WITH"))
            ):
                logger.info("Non-SELECT queries - validating execution success")
                return True

            # Compare result sets
            if len(original_results) != len(optimized_results):
                logger.warning(
                    f"Different result counts: {len(original_results)} vs {len(optimized_results)}"
                )
                return False

            # Sort results for comparison (handle cases where order might differ)
            original_sorted = self._sort_results(original_results)
            optimized_sorted = self._sort_results(optimized_results)

            # Compare row by row
            for i, (orig_row, opt_row) in enumerate(
                zip(original_sorted, optimized_sorted)
            ):
                if not self._compare_rows(orig_row, opt_row):
                    logger.warning(f"Row {i} differs between queries")
                    return False

            logger.info("✅ Queries produce equivalent results")
            return True

        except Exception as e:
            logger.error(f"Error validating query equivalence: {str(e)}")
            return False

    async def compare_performance(
        self,
        original_query: str,
        optimized_query: str,
        db_connection: DatabaseConnection,
        iterations: int = 3,
    ) -> dict[str, float]:
        """Compare performance of two queries."""
        try:
            logger.info(f"Comparing query performance over {iterations} iterations...")

            # Measure original query performance
            original_time = await db_connection.measure_query_performance(
                original_query, iterations
            )

            # Measure optimized query performance
            optimized_time = await db_connection.measure_query_performance(
                optimized_query, iterations
            )

            # Calculate improvement
            improvement_percent = 0.0
            if original_time > 0 and original_time != float("inf"):
                improvement_percent = (
                    (original_time - optimized_time) / original_time
                ) * 100

            results = {
                "original_time_ms": original_time,
                "optimized_time_ms": optimized_time,
                "improvement_percent": improvement_percent,
                "is_faster": optimized_time < original_time,
            }

            logger.info(
                f"Performance comparison complete: {improvement_percent:.2f}% improvement"
            )
            return results

        except Exception as e:
            logger.error(f"Error comparing query performance: {str(e)}")
            return {
                "original_time_ms": float("inf"),
                "optimized_time_ms": float("inf"),
                "improvement_percent": 0.0,
                "is_faster": False,
            }

    def _sort_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort results for consistent comparison."""
        if not results:
            return results

        try:
            # Create a hash for each row for sorting
            def row_hash(row: Dict[str, Any]) -> str:
                row_str = str(sorted(row.items()))
                return hashlib.md5(row_str.encode()).hexdigest()

            return sorted(results, key=row_hash)
        except Exception:
            # If sorting fails, return as-is
            return results

    def _compare_rows(self, row1: Dict[str, Any], row2: Dict[str, Any]) -> bool:
        """Compare two result rows for equality."""
        if set(row1.keys()) != set(row2.keys()):
            return False

        for key in row1.keys():
            val1, val2 = row1[key], row2[key]

            # Handle None values
            if val1 is None and val2 is None:
                continue
            if val1 is None or val2 is None:
                return False

            # Handle numeric comparisons with tolerance
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if abs(val1 - val2) > 1e-6:  # Small tolerance for floating point
                    return False
            else:
                if str(val1) != str(val2):
                    return False

        return True
