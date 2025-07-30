import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from typer import Argument, Option, Typer

from config.config import OptimizerConfig
from config.logger import logger
from core.client import LLMClientFactory
from core.types import DatabaseType
from infra.file_handler import LocalFileHandler
from infra.metadata_repository import JsonMetadataRepository
from services.query_optimizer import DatabaseQueryOptimizer

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


@app.command()
def compare(
    sql_file: Path = Argument(..., help="Path to SQL file to optimize"),
    provider: str = Option("gemini", help="LLM provider (gemini/openai/claude)"),
    model: str | None = Option(None, help="Model name to use"),
    api_key: str | None = Option(None, help="API key for LLM provider"),
) -> None:
    """Compare optimization results for both Oracle and SQLite."""
    asyncio.run(_compare_async(sql_file, provider, model, api_key))


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


async def _compare_async(
    sql_file: Path,
    provider: str,
    model: str | None,
    api_key: str | None,
) -> None:
    """Compare optimization results for both database types."""
    try:
        print(f"\n🔍 Comparing optimizations for {sql_file}")
        print("=" * 60)

        results = {}
        # Optimize for both database types
        for db_type in [DatabaseType.ORACLE, DatabaseType.SQLITE]:
            print(f"\n⚙️  Optimizing for {db_type.value.upper()}...")
            if provider == "oracle_genai":
                config = OptimizerConfig(
                    provider=provider,
                    database_type=db_type,
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
            else:
                config = OptimizerConfig(
                    provider=provider,
                    database_type=db_type,
                    api_key=api_key or LLMClientFactory._get_api_key_from_env(provider),
                    model_name=model or None,
                )

            results[db_type] = await DatabaseQueryOptimizer(
                llm_client=LLMClientFactory.create_client(config, api_key),
                file_handler=LocalFileHandler(),
                metadata_repo=JsonMetadataRepository(),
                config=config,
                database_type=db_type,
            ).optimize_query(sql_file)

        print("\n📊 Comparison Results:")
        print("=" * 60)

        for db_type, result in results.items():
            print(f"\n🗄️  {db_type.value.upper()}:")
            print(f"   📝 Explanation length: {len(result.explained_query)} chars")
            print(f"   ⚡ Query length: {len(result.optimized_query)} chars")
            print(f"   📊 Version: {result.metadata.version}")
            print(
                f"   💾 Saved to: {sql_file.parent / f'{sql_file.stem}_{db_type.value}_optimization.json'}"
            )
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app()
