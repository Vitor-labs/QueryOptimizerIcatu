"""Output formatters for CLI commands.

This module provides formatting utilities for displaying optimization
results, comparisons, and other CLI output in a user-friendly way.
"""

from datetime import datetime
from pathlib import Path

from application.dto.optimization_dto import ComparisonDTO, OptimizationDTO


class OutputFormatter:
	"""Formatter for CLI output with consistent styling.

	Provides methods to format various types of output including
	optimization results, comparisons, and progress indicators.

	Examples:
		>>> formatter = OutputFormatter()
		>>> formatter.print_optimization_result(result_dto, verbose=True)
	"""

	@staticmethod
	def print_header(title: str) -> None:
		"""Print a formatted header.

		Args:
			title: Header title text
		"""
		print(f"\n{'=' * 70}")
		print(f"  {title}")
		print(f"{'=' * 70}")

	@staticmethod
	def print_section(title: str) -> None:
		"""Print a section divider.

		Args:
			title: Section title
		"""
		print(f"\n{title}")
		print(f"{'-' * len(title)}")

	@staticmethod
	def print_optimization_result(
		result: OptimizationDTO,
		sql_file: Path,
		verbose: bool = False,
	) -> None:
		"""Print optimization result in formatted style.

		Args:
			result: Optimization result DTO
			sql_file: Original SQL file path
			verbose: Whether to show full query details
		"""
		OutputFormatter.print_header(
			f"🎯 {result.database_type.upper()} Optimization Results"
		)

		# Basic information
		print(f"\n📄 Original Query File: {sql_file}")
		print(f"🗄️  Database Type: {result.database_type.upper()}")
		print(f"📊 Version: {result.version}")
		print(
			f"⏰ Optimized At: {OutputFormatter._format_datetime(result.optimized_at)}"
		)
		print(f"🔑 Query Hash: {result.query_hash}")

		# Explanation preview
		OutputFormatter.print_section("📝 Query Explanation")
		explanation_preview = OutputFormatter._truncate_text(
			result.explanation,
			200 if not verbose else None,
		)
		print(f"{explanation_preview}")

		# Optimized query preview
		OutputFormatter.print_section("⚡ Optimized Query")
		if verbose:
			print(result.optimized_query)
		else:
			query_preview = OutputFormatter._truncate_text(result.optimized_query, 200)
			print(f"{query_preview}")
			print("\n💡 Use --verbose to see the full query")

		# Output file location
		output_file = sql_file.with_name(
			f"{sql_file.stem}_{result.database_type}_optimization.json"
		)
		print(f"\n💾 Full results saved to: {output_file}")
		print()

	@staticmethod
	def print_comparison_result(
		comparison: ComparisonDTO,
		sql_file: Path,
	) -> None:
		"""Print comparison results for multiple databases.

		Args:
			comparison: Comparison DTO with results for multiple databases
			sql_file: Original SQL file path
		"""
		OutputFormatter.print_header("🔍 Multi-Database Optimization Comparison")

		print(f"\n📄 Original Query File: {sql_file}")
		print(
			f"🗄️  Databases Compared: {', '.join(comparison.database_types()).upper()}"
		)

		# Original query
		OutputFormatter.print_section("📋 Original Query")
		query_preview = OutputFormatter._truncate_text(comparison.original_query, 150)
		print(f"{query_preview}")

		# Results for each database
		for db_type in sorted(comparison.database_types()):
			result = comparison.optimizations[db_type]

			OutputFormatter.print_section(f"🗄️  {db_type.upper()} Results")
			print(f"   Version: {result.version}")
			print(f"   Query Hash: {result.query_hash}")
			print(f"   Explanation Length: {len(result.explanation)} chars")
			print(f"   Optimized Query Length: {len(result.optimized_query)} chars")

			output_file = sql_file.with_name(
				f"{sql_file.stem}_{db_type}_optimization.json"
			)
			print(f"   Saved to: {output_file}")

		# Comparison summary file
		comparison_file = sql_file.with_name(f"{sql_file.stem}_comparison.json")
		print(f"\n💾 Comparison summary saved to: {comparison_file}")
		print()

	@staticmethod
	def print_progress(message: str) -> None:
		"""Print a progress message.

		Args:
			message: Progress message to display
		"""
		print(f"\n⚙️  {message}...", flush=True)

	@staticmethod
	def print_success(message: str) -> None:
		"""Print a success message.

		Args:
			message: Success message to display
		"""
		print(f"\n✅ {message}")

	@staticmethod
	def _truncate_text(text: str, max_length: int | None = None) -> str:
		"""Truncate text to maximum length with ellipsis.

		Args:
			text: Text to truncate
			max_length: Maximum length (None for no truncation)

		Returns:
			Truncated text with ellipsis if needed
		"""
		if max_length is None or len(text) <= max_length:
			return text

		return f"{text[:max_length]}..."

	@staticmethod
	def _format_datetime(dt: datetime) -> str:
		"""Format datetime for display.

		Args:
			dt: Datetime to format

		Returns:
			Formatted datetime string
		"""
		return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


class TableFormatter:
	"""Formatter for tabular data output.

	Provides utilities for creating aligned tables for CLI output.

	Examples:
		>>> table = TableFormatter(["Name", "Value", "Status"])
		>>> table.add_row(["Option 1", "123", "✓"])
		>>> table.print()
	"""

	def __init__(self, headers: list[str]) -> None:
		"""Initialize table formatter.

		Args:
			headers: Column headers
		"""
		self._headers = headers
		self._rows: list[list[str]] = []
		self._col_widths: list[int] = [len(h) for h in headers]

	def add_row(self, row: list[str]) -> None:
		"""Add a row to the table.

		Args:
			row: List of column values
		"""
		if len(row) != len(self._headers):
			raise ValueError(
				f"Row has {len(row)} columns, expected {len(self._headers)}"
			)

		# Update column widths
		for i, value in enumerate(row):
			self._col_widths[i] = max(self._col_widths[i], len(value))

		self._rows.append(row)

	def print(self) -> None:
		"""Print the formatted table."""
		# Print header
		header_line = " | ".join(
			h.ljust(w) for h, w in zip(self._headers, self._col_widths)
		)
		print(f"\n{header_line}")
		print("-" * len(header_line))

		# Print rows
		for row in self._rows:
			row_line = " | ".join(v.ljust(w) for v, w in zip(row, self._col_widths))
			print(row_line)

		print()
