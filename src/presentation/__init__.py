"""Presentation layer for SQL Query Optimizer.

The presentation layer handles user interaction through the CLI.
It depends on the application layer but is independent of infrastructure details.

This layer includes:
- CLI commands and argument parsing
- Output formatting and display
- Error handling and user feedback
- DTO to display model mapping
"""

from presentation.cli.commands import app, main
from presentation.cli.error_handler import CLIErrorHandler
from presentation.cli.formatters import OutputFormatter

__all__ = ["app", "main", "CLIErrorHandler", "OutputFormatter"]
