"""Error handling for CLI commands.

This module provides user-friendly error handling and formatting
for CLI operations, translating domain/application errors into
readable messages.
"""

import sys
from typing import NoReturn

from domain.exceptions.domain_exceptions import (
	DomainError,
	InvalidDatabaseTypeError,
	LLMProviderError,
	OptimizationError,
	QueryValidationError,
)
from infrastructure.config.logger import get_logger

logger = get_logger(__name__)


class CLIErrorHandler:
	"""Handler for CLI errors with user-friendly formatting.

	This class translates exceptions into user-friendly error messages
	and handles program exit with appropriate status codes.

	Examples:
		>>> try:
		...     await use_case.execute(path)
		... except Exception as e:
		...     CLIErrorHandler.handle_error(e)
	"""

	@staticmethod
	def handle_error(error: Exception, verbose: bool = False) -> NoReturn:
		"""Handle error and exit program with appropriate status code.

		Args:
			error: Exception that occurred
			verbose: Whether to show detailed error information

		Raises:
			SystemExit: Always exits with appropriate status code
		"""
		# Log the full error
		logger.error(
			"CLI operation failed",
			error_type=type(error).__name__,
			error=str(error),
		)

		# Determine error message and exit code
		exit_code = 1
		message = CLIErrorHandler._format_error_message(error)

		# Print user-friendly error
		print(f"\n❌ Error: {message}", file=sys.stderr)

		# Print detailed error in verbose mode
		if verbose:
			print("\n📋 Details:", file=sys.stderr)
			print(f"   Type: {type(error).__name__}", file=sys.stderr)
			print(f"   Message: {str(error)}", file=sys.stderr)

			# Print stack trace if available
			import traceback

			print("\n🔍 Stack Trace:", file=sys.stderr)
			traceback.print_exc(file=sys.stderr)

		raise SystemExit(exit_code)

	@staticmethod
	def _format_error_message(error: Exception) -> str:
		"""Format error into user-friendly message.

		Args:
			error: Exception to format

		Returns:
			User-friendly error message
		"""
		# Handle specific domain errors
		if isinstance(error, QueryValidationError):
			return f"Invalid SQL query: {error}"

		if isinstance(error, InvalidDatabaseTypeError):
			return f"Invalid database type: {error}"

		if isinstance(error, LLMProviderError):
			return f"LLM provider error: {error}"

		if isinstance(error, OptimizationError):
			return f"Optimization failed: {error}"

		if isinstance(error, DomainError):
			return f"Domain error: {error}"

		# Handle common errors
		if isinstance(error, FileNotFoundError):
			return f"File not found: {error}"

		if isinstance(error, PermissionError):
			return f"Permission denied: {error}"

		if isinstance(error, ValueError):
			return f"Invalid value: {error}"

		if isinstance(error, KeyError):
			return f"Missing required configuration: {error}"

		# Generic error
		return str(error) or "An unexpected error occurred"

	@staticmethod
	def print_warning(message: str) -> None:
		"""Print a warning message to stderr.

		Args:
			message: Warning message to print
		"""
		print(f"\n⚠️  Warning: {message}", file=sys.stderr)
		logger.warning(message)

	@staticmethod
	def print_info(message: str) -> None:
		"""Print an informational message.

		Args:
			message: Info message to print
		"""
		print(f"\nℹ️  {message}")
