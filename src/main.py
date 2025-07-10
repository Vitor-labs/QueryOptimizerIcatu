# src/main.py
import asyncio
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv

from config.config import OptimizerConfig
from config.logger import logger
from core.client import LLMClientFactory
from infra.file_handler import LocalFileHandler
from infra.metadata_repository import JsonMetadataRepository
from services.query_optimizer import OracleQueryOptimizer

load_dotenv()

app = typer.Typer(help="Oracle SQL Query Optimizer")


@app.command()
def optimize(
    sql_file: Path = typer.Argument(..., help="Path to SQL file to optimize"),
    provider: str = typer.Option("gemini", help="LLM provider (gemini/openai/claude)"),
    model: str | None = typer.Option(None, help="Model name to use"),
    api_key: str | None = typer.Option(None, help="API key for LLM provider"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Optimize a SQL query from file."""
    asyncio.run(_optimize_async(sql_file, provider, model, api_key, verbose))


async def _optimize_async(
    sql_file: Path,
    provider: str,
    model: str | None,
    api_key: str | None,
    verbose: bool,
) -> None:
    """Async optimization implementation."""
    try:
        # Setup configuration
        config = OptimizerConfig(provider=provider)
        if model:
            config.model_name = model

        # Initialize components
        llm_client = LLMClientFactory.create_client(config, api_key)
        file_handler = LocalFileHandler()
        metadata_repo = JsonMetadataRepository()

        # Create optimizer
        optimizer = OracleQueryOptimizer(
            llm_client=llm_client,
            file_handler=file_handler,
            metadata_repo=metadata_repo,
            config=config,
        )

        # Perform optimization
        result = await optimizer.optimize_query(sql_file)

        # Display results
        print("\n🎯 Optimization Results:")
        print("=" * 50)
        print(f"📄 Original Query: {sql_file}")
        print(f"📝 Explanation: {result.explained_query[:100]}...")
        print(f"⚡ Optimized Query Preview: {result.optimized_query[:100]}...")
        print(f"📊 Version: {result.metadata.version}")
        print(f"⏰ Last Optimization: {result.metadata.last_optimization}")

        output_file = sql_file.parent / f"{sql_file.stem}_optimization.json"
        print(f"💾 Full results saved to: {output_file}")

        if verbose:
            print("\n📋 Full Optimized Query:")
            print("-" * 30)
            print(result.optimized_query)

    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app()
