"""CLI commands for SQL Query Optimizer.

This module defines the command-line interface using Typer,
providing commands for optimizing and comparing SQL queries.
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from typer import Argument, Option, Typer

from application.use_cases.compare_optimizations import CompareOptimizationsUseCase
from application.use_cases.optimize_query import OptimizeQueryUseCase
from domain.value_objects.database_type import DatabaseType
from infrastructure.config.logger import configure_logging, get_logger
from infrastructure.config.settings import Settings
from infrastructure.llm.factory import LLMAdapterFactory
from infrastructure.persistence.file_handler import LocalFileHandler
from infrastructure.persistence.metadata_repository import JsonMetadataRepository
from infrastructure.prompts.factory import PromptGeneratorFactory
from presentation.cli.error_handler import CLIErrorHandler
from presentation.cli.formatters import OutputFormatter

# Load environment variables
load_dotenv()

# Create Typer app
app = Typer(
	name="sql-optimizer",
	help="Database SQL Query Optimizer using LLM technology",
	add_completion=False,
)

logger = get_logger(__name__)


@app.command()
def optimize(
	sql_file: Path = Argument(
		...,
		help="Path to SQL file to optimize",
		exists=True,
		file_okay=True,
		dir_okay=False,
		readable=True,
	),
	database: str = Option(
		"oracle",
		"--database",
		"-d",
		help="Database type (oracle/sqlite/sqlserver/postgresql/mysql)",
	),
	provider: str = Option(
		"gemini",
		"--provider",
		"-p",
		help="LLM provider (gemini/openai/claude/oracle_genai)",
	),
	model: str | None = Option(
		None,
		"--model",
		"-m",
		help="Model name to use (uses provider default if not specified)",
	),
	api_key: str | None = Option(
		None,
		"--api-key",
		"-k",
		help="API key for LLM provider (can also use environment variables)",
	),
	temperature: float = Option(
		0.1,
		"--temperature",
		"-t",
		help="LLM temperature (0.0-1.0, lower is more deterministic)",
		min=0.0,
		max=1.0,
	),
	max_tokens: int = Option(
		8192,
		"--max-tokens",
		help="Maximum tokens to generate",
		min=100,
	),
	verbose: bool = Option(
		False,
		"--verbose",
		"-v",
		help="Enable verbose output including full queries",
	),
	log_level: str = Option(
		"INFO",
		"--log-level",
		help="Logging level (DEBUG/INFO/WARNING/ERROR)",
	),
) -> None:
	"""Optimize a SQL query for a specific database type.

	This command reads a SQL file, uses an LLM to understand and optimize
	the query for the specified database system, and saves the results.

	Examples:
		# Optimize for Oracle using Gemini
		$ sql-optimizer optimize query.sql --database oracle

		# Optimize for SQLite using OpenAI with custom model
		$ sql-optimizer optimize query.sql -d sqlite -p openai -m gpt-4-turbo

		# Verbose output with custom temperature
		$ sql-optimizer optimize query.sql -v -t 0.2
	"""
	# Configure logging
	configure_logging(log_level=log_level)

	# Run async optimization
	asyncio.run(
		_execute_optimization(
			sql_file=sql_file,
			database=database,
			provider=provider,
			model=model,
			api_key=api_key,
			temperature=temperature,
			max_tokens=max_tokens,
			verbose=verbose,
		)
	)


@app.command()
def compare(
	sql_file: Path = Argument(
		...,
		help="Path to SQL file to optimize",
		exists=True,
		file_okay=True,
		dir_okay=False,
		readable=True,
	),
	databases: str | None = Option(
		None,
		"--databases",
		"-d",
		help="Comma-separated list of databases (e.g., oracle,sqlite,sqlserver)",
	),
	provider: str = Option(
		"gemini",
		"--provider",
		"-p",
		help="LLM provider (gemini/openai/claude/oracle_genai)",
	),
	model: str | None = Option(
		None,
		"--model",
		"-m",
		help="Model name to use",
	),
	api_key: str | None = Option(
		None,
		"--api-key",
		"-k",
		help="API key for LLM provider",
	),
	temperature: float = Option(
		0.1,
		"--temperature",
		"-t",
		help="LLM temperature (0.0-1.0)",
		min=0.0,
		max=1.0,
	),
	max_tokens: int = Option(
		8192,
		"--max-tokens",
		help="Maximum tokens to generate",
		min=100,
	),
	log_level: str = Option(
		"INFO",
		"--log-level",
		help="Logging level (DEBUG/INFO/WARNING/ERROR)",
	),
) -> None:
	"""Compare optimizations across multiple database types.

	This command optimizes the same SQL query for multiple database systems
	and provides a comparison of the results.

	Examples:
		# Compare Oracle and SQLite optimizations
		$ sql-optimizer compare query.sql --databases oracle,sqlite

		# Compare all supported databases
		$ sql-optimizer compare query.sql

		# Compare with custom provider and model
		$ sql-optimizer compare query.sql -d oracle,sqlserver -p openai -m gpt-4
	"""
	# Configure logging
	configure_logging(log_level=log_level)

	# Parse database list
	database_types = None
	if databases:
		try:
			database_types = [
				DatabaseType.from_string(db.strip()) for db in databases.split(",")
			]
		except ValueError as e:
			CLIErrorHandler.handle_error(e)

	# Run async comparison
	asyncio.run(
		_execute_comparison(
			sql_file=sql_file,
			database_types=database_types,
			provider=provider,
			model=model,
			api_key=api_key,
			temperature=temperature,
			max_tokens=max_tokens,
		)
	)


@app.command()
def list_databases() -> None:
	"""List all supported database types.

	Shows which database systems are supported by the optimizer.
	"""
	print("\n📚 Supported Database Types:")
	print("=" * 50)

	for db_type in DatabaseType:
		features = []
		if db_type.supports_hints():
			features.append("hints")
		if db_type.supports_cte():
			features.append("CTEs")
		if db_type.supports_window_functions():
			features.append("window functions")

		feature_str = ", ".join(features) if features else "basic SQL"
		print(f"  • {db_type.value:12} - {db_type.display_name:15} ({feature_str})")

	print()


@app.command()
def list_providers() -> None:
	"""List all supported LLM providers.

	Shows which LLM providers are available and their requirements.
	"""
	print("\n🤖 Supported LLM Providers:")
	print("=" * 50)

	for provider_id, name, env_var, default_model in [
		("gemini", "Google Gemini", "GOOGLE_API_KEY", "gemini-2.0-flash-exp"),
		("openai", "OpenAI GPT", "OPENAI_API_KEY", "gpt-4"),
		(
			"claude",
			"Anthropic Claude",
			"ANTHROPIC_API_KEY",
			"claude-3-5-sonnet-20241022",
		),
		(
			"oracle_genai",
			"Oracle GenAI",
			"OCI_COMPARTMENT_ID, OCI_MODEL_ID",
			"cohere.command-r-plus",
		),
	]:
		print(f"\n  • {provider_id}")
		print(f"    Name: {name}")
		print(f"    Environment: {env_var}")
		print(f"    Default Model: {default_model}")

	print()


async def _execute_optimization(
	sql_file: Path,
	database: str,
	provider: str,
	model: str | None,
	api_key: str | None,
	temperature: float,
	max_tokens: int,
	verbose: bool,
) -> None:
	"""Execute single database optimization.

	Args:
		sql_file: Path to SQL file
		database: Database type string
		provider: LLM provider name
		model: Optional model name
		api_key: Optional API key
		temperature: LLM temperature
		max_tokens: Maximum tokens
		verbose: Verbose output flag
	"""
	try:
		database_type = DatabaseType.from_string(database)
		settings = Settings.from_cli_args(
			provider=provider,
			database=database.lower(),
			model=model,
			api_key=api_key,
			temperature=temperature,
			max_tokens=max_tokens,
		)
		logger.info(
			"Starting optimization",
			file=str(sql_file),
			database=database_type.value,
			provider=provider,
			model=settings.effective_model_name,
		)
		OutputFormatter.print_progress(f"Optimizing for {database_type.display_name}")
		OutputFormatter.print_optimization_result(
			await OptimizeQueryUseCase(
				llm_adapter=LLMAdapterFactory.create(settings),
				file_handler=LocalFileHandler(),
				metadata_repository=JsonMetadataRepository(),
				prompt_generator=PromptGeneratorFactory.create(database_type),
			).execute(
				sql_file=sql_file,
				database_type=database_type,
				temperature=temperature,
				max_tokens=max_tokens,
			),
			sql_file,
			verbose,
		)
		OutputFormatter.print_success("Optimization completed successfully")

	except Exception as e:
		CLIErrorHandler.handle_error(e, verbose)


async def _execute_comparison(
	sql_file: Path,
	database_types: list[DatabaseType] | None,
	provider: str,
	model: str | None,
	api_key: str | None,
	temperature: float,
	max_tokens: int,
) -> None:
	"""Execute multi-database comparison.

	Args:
		sql_file: Path to SQL file
		database_types: List of database types to compare (None for all)
		provider: LLM provider name
		model: Optional model name
		api_key: Optional API key
		temperature: LLM temperature
		max_tokens: Maximum tokens
	"""
	try:
		logger.info(
			"Starting comparison",
			file=str(sql_file),
			databases=database_types or "all",
			provider=provider,
		)
		# Create and execute use case
		db_list = database_types or list(DatabaseType)
		OutputFormatter.print_progress(
			f"Comparing optimizations for {len(db_list)} databases"
		)
		OutputFormatter.print_comparison_result(
			await CompareOptimizationsUseCase(
				llm_adapter=LLMAdapterFactory.create(
					# database type doesn't matter for comparison
					Settings.from_cli_args(
						provider=provider,
						database="oracle",  # Default, not used in comparison
						model=model,
						api_key=api_key,
						temperature=temperature,
						max_tokens=max_tokens,
					)
				),
				file_handler=LocalFileHandler(),
				metadata_repository=JsonMetadataRepository(),
				prompt_generator_factory=PromptGeneratorFactory,
			).execute(
				sql_file=sql_file,
				database_types=database_types,
				temperature=temperature,
				max_tokens=max_tokens,
			),
			sql_file,
		)
		OutputFormatter.print_success("Comparison completed successfully")

	except Exception as e:
		CLIErrorHandler.handle_error(e, verbose=True)


def main() -> None:
	"""Main entry point for CLI application."""
	app()


if __name__ == "__main__":
	main()
