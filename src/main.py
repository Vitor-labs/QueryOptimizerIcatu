import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from infrastructure.database_connections import DatabaseConnectionFactory
from infrastructure.file_handler import LocalFileHandler
from infrastructure.metadata_repository import JsonMetadataRepository
from llm.clients import LLMClientFactory
from typer import Argument, Choice, Option, Typer

from config.config import OptimizerConfig
from config.logger import logger
from core.types import DatabaseType
from services.query_optimizer import DatabaseQueryOptimizer
from services.query_validator import DatabaseQueryValidator

load_dotenv()

app = Typer(help="Database SQL Query Optimizer")


@app.command()
def optimize(
    sql_file: Path = Argument(..., help="Path to SQL file to optimize"),
    database: str = Option("oracle", help="Database type (oracle/sqlite)"),
    provider: str = Option("gemini", help="LLM provider (gemini/openai/claude)"),
    model: str | None = Option(None, help="Model name to use"),
    api_key: str | None = Option(None, help="API key for LLM provider"),
    verbose: bool = Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Optimize a SQL query from file for specified database type."""
    asyncio.run(_optimize_async(sql_file, database, provider, model, api_key, verbose))


async def _optimize_async(
    sql_file: Path,
    database: str,
    provider: str,
    model: str | None,
    api_key: str | None,
    verbose: bool,
) -> None:
    """Async optimization implementation."""
    try:
        database_type = DatabaseType(database.lower())
        config = (
            OptimizerConfig(
                provider=provider,
                database_type=database_type,
                model_name=model or "cohere.command",
                max_output_tokens=4000,
                extra={
                    "compartment_id": os.getenv("OCI_COMPARTMENT_ID", ""),
                    "model_id": os.getenv("OCI_MODEL_ID", "cohere.command"),
                    "endpoint": os.getenv(
                        "OCI_GENAI_ENDPOINT",
                        "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
                    ),
                    "oci_profile": os.getenv("OCI_PROFILE", "DEFAULT"),
                },
            )
            if provider == "oracle_genai"
            else OptimizerConfig(
                provider=provider,
                database_type=database_type,
                api_key=api_key or LLMClientFactory._get_api_key_from_env(provider),
                model_name=model or None,
            )
        )

        result = await DatabaseQueryOptimizer(
            llm_client=LLMClientFactory.create_client(config, api_key),
            file_handler=LocalFileHandler(),
            metadata_repo=JsonMetadataRepository(),
            config=config,
            database_type=database_type,
        ).optimize_query(sql_file)

        print(f"\n🎯 {database_type.value.upper()} Optimization Results:")
        print("=" * 60)
        print(f"📄 Original Query: {sql_file}")
        print(f"🗄️  Database Type: {database_type.value.upper()}")
        print(f"📝 Explanation: {result.explained_query[:100]}...")
        print(f"⚡ Optimized Query Preview: {result.optimized_query[:100]}...")
        print(f"📊 Version: {result.metadata.version}")
        print(f"⏰ Last Optimization: {result.metadata.last_optimization}")
        print(
            f"💾 Full results saved to: {sql_file.parent / f'{sql_file.stem}_{database_type.value}_optimization.json'}"
        )
        if verbose:
            print(f"\n📋 Full {database_type.value.upper()} Optimized Query:")
            print("-" * 40)
            print(result.optimized_query)

    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


@app.command()
def compare(
    sql_file: Path = Argument(..., help="Path to SQL file to optimize"),
    database: str = Option(
        "sqlite",
        help="Database type (oracle/sqlite)",
        click_type=Choice(["oracle", "sqlite"], case_sensitive=False),
    ),
    provider: str = Option("gemini", help="LLM provider (gemini/openai/claude)"),
    model: str | None = Option(None, help="Model name to use"),
    api_key: str | None = Option(None, help="API key for LLM provider"),
    db_path: str | None = Option(
        None, help="Database path (SQLite) or connection string (Oracle)"
    ),
    iterations: int = Option(3, help="Number of iterations for performance testing"),
) -> None:
    """Compare original vs optimized query performance and validate results."""
    asyncio.run(
        _compare_async(
            sql_file, database, provider, model, api_key, db_path, iterations
        )
    )


async def _compare_async(
    sql_file: Path,
    database: str,
    provider: str,
    model: str | None,
    api_key: str | None,
    db_path: str | None,
    iterations: int,
) -> None:
    """Compare optimization results with performance validation."""
    try:
        # Parse database type
        database_type = DatabaseType(database.lower())

        print(f"\n🔍 Performance Comparison for {sql_file}")
        print(f"🗄️  Database: {database_type.value.upper()}")
        print("=" * 70)

        # Setup configuration
        config = OptimizerConfig(provider=provider, database_type=database_type)
        if model:
            config.model_name = model

        # Set database connection parameters
        if db_path:
            if database_type == DatabaseType.SQLITE:
                config.database_connection_params = {"database_path": db_path}
            elif database_type == DatabaseType.ORACLE:
                config.database_connection_params = {"connection_string": db_path}

        # Initialize components
        llm_client = LLMClientFactory.create_client(config, api_key)
        file_handler = LocalFileHandler()
        metadata_repo = JsonMetadataRepository()

        # Create optimizer
        optimizer = DatabaseQueryOptimizer(
            llm_client=llm_client,
            file_handler=file_handler,
            metadata_repo=metadata_repo,
            config=config,
            database_type=database_type,
        )

        # Perform optimization
        print("⚙️  Generating optimized query...")
        result = await optimizer.optimize_query(sql_file)

        # Setup database connection
        db_connection = DatabaseConnectionFactory.create_connection(
            database_type, config.database_connection_params
        )

        try:
            await db_connection.connect()

            # Initialize validator
            validator = DatabaseQueryValidator()

            # Step 1: Validate query equivalence
            print("\n🔍 Validating query equivalence...")
            is_equivalent = await validator.validate_queries_equivalent(
                result.original_query, result.optimized_query, db_connection
            )

            if not is_equivalent:
                print("❌ WARNING: Queries produce different results!")
                print("   The optimization may have changed the query semantics.")
            else:
                print("✅ Queries produce equivalent results")

            # Step 2: Compare performance
            print(f"\n⏱️  Measuring performance ({iterations} iterations)...")
            performance = await validator.compare_performance(
                result.original_query, result.optimized_query, db_connection, iterations
            )

            # Display results
            print("\n📊 Performance Results:")
            print("-" * 40)
            print(f"Original Query Time:   {performance['original_time_ms']:.2f} ms")
            print(f"Optimized Query Time:  {performance['optimized_time_ms']:.2f} ms")

            if performance["is_faster"]:
                print(
                    f"🚀 Improvement:        {performance['improvement_percent']:.2f}% faster"
                )
            else:
                print(
                    f"⚠️  Regression:         {abs(performance['improvement_percent']):.2f}% slower"
                )

            # Overall assessment
            print("\n🎯 Overall Assessment:")
            print("-" * 30)

            if is_equivalent and performance["is_faster"]:
                print("✅ SUCCESS: Optimization is valid and faster!")
            elif is_equivalent and not performance["is_faster"]:
                print("⚠️  NEUTRAL: Optimization is valid but not faster")
            elif not is_equivalent and performance["is_faster"]:
                print("❌ FAILED: Optimization is faster but changes results")
            else:
                print("❌ FAILED: Optimization changes results and is slower")

            # Save detailed results
            output_file = (
                sql_file.parent
                / f"{sql_file.stem}_{database_type.value}_comparison.json"
            )
            comparison_data = {
                **result.metadata.to_dict(),
                "performance_comparison": performance,
                "queries_equivalent": is_equivalent,
                "original_query": result.original_query,
                "optimized_query": result.optimized_query,
            }

            await file_handler.write_json_file(output_file, comparison_data)
            print(f"\n💾 Detailed results saved to: {output_file}")

        finally:
            await db_connection.disconnect()

    except Exception as e:
        logger.error(f"Performance comparison failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app()
