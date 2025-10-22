"""CLI interface for SQL Query Optimizer.

This module provides the command-line interface including commands,
formatters, and error handling.
"""

from presentation.cli.commands import app, main
from presentation.cli.error_handler import CLIErrorHandler
from presentation.cli.formatters import OutputFormatter, TableFormatter

__all__ = ["app", "main", "CLIErrorHandler", "OutputFormatter", "TableFormatter"]
