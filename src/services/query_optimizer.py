# src/services/query_optimizer.py (updated)
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from config.config import OptimizerConfig
from config.logger import logger
from core.interfaces import FileHandler, LLMClient, MetadataRepository, QueryOptimizer
from core.types import DatabaseType, OptimizationResult, QueryMetadata
from services.prompt_generator import PromptGeneratorFactory


class DatabaseQueryOptimizer(QueryOptimizer):
    """Database-agnostic query optimizer implementation."""

    def __init__(
        self,
        llm_client: LLMClient,
        file_handler: FileHandler,
        metadata_repo: MetadataRepository,
        config: OptimizerConfig,
        database_type: DatabaseType,
    ) -> None:
        """Initialize optimizer with dependencies."""
        self._llm_client = llm_client
        self._file_handler = file_handler
        self._metadata_repo = metadata_repo
        self._config = config
        self._database_type = database_type
        self._prompt_generator = PromptGeneratorFactory.create_generator(database_type)

    async def optimize_query(self, sql_file_path: Path) -> OptimizationResult:
        """Optimize a SQL query from file."""
        logger.info(
            f"Starting {self._database_type.value.upper()} optimization for: {sql_file_path}"
        )
        try:
            original_query = await self._file_handler.read_sql_file(sql_file_path)
            query_hash = self._generate_query_hash(original_query)
            metadata = await self._get_or_create_metadata(query_hash, original_query)

            logger.info("Converting SQL to natural language...")
            explanation = await self._sql_to_natural_language(original_query)

            logger.info("Converting natural language to optimized SQL...")
            optimized_query = await self._natural_language_to_sql(explanation)

            metadata.explanation_text = explanation
            metadata.last_optimization = datetime.now()
            metadata.database_type = self._database_type

            await self._metadata_repo.save_metadata(query_hash, metadata)
            await self._generate_output_json(sql_file_path, metadata)

            logger.info(
                f"{self._database_type.value.upper()} optimization completed successfully"
            )
            return OptimizationResult(
                original_query=original_query,
                explained_query=explanation,
                optimized_query=optimized_query,
                metadata=metadata,
                database_type=self._database_type,
            )
        except Exception as e:
            logger.error(
                f"Error during {self._database_type.value} optimization: {str(e)}"
            )
            raise

    async def _sql_to_natural_language(self, sql_query: str) -> str:
        """Convert SQL query to natural language explanation."""
        return await self._llm_client.generate_response(
            self._prompt_generator.generate_sql_to_natural_prompt(sql_query),
            {
                "model_name": self._config.model_name,
                "temperature": self._config.temperature,
                "max_output_tokens": self._config.max_output_tokens,
            },
        )

    async def _natural_language_to_sql(self, explanation: str) -> str:
        """Convert natural language explanation to optimized SQL."""
        return await self._llm_client.generate_response(
            self._prompt_generator.generate_natural_to_sql_prompt(explanation),
            {
                "model_name": self._config.model_name,
                "temperature": self._config.temperature,
                "max_output_tokens": self._config.max_output_tokens,
            },
        )

    async def _get_or_create_metadata(
        self, query_hash: str, query: str
    ) -> QueryMetadata:
        """Get existing metadata or create new."""
        if existing_metadata := await self._metadata_repo.get_metadata(query_hash):
            # Increment version
            version_parts = existing_metadata.version.split(".")
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            existing_metadata.version = ".".join(version_parts)
            existing_metadata.database_type = self._database_type  # Update if changed
            return existing_metadata

        return QueryMetadata(
            query_sql=query,
            explanation_text="",
            version="0.0",
            last_optimization=datetime.now(),
            database_type=self._database_type,
        )

    async def _generate_output_json(
        self, sql_file_path: Path, metadata: QueryMetadata
    ) -> None:
        """Generate JSON output file."""
        await self._file_handler.write_json_file(
            (
                sql_file_path.parent
                / f"{sql_file_path.stem}_{self._database_type.value}_optimization.json"
            ),
            metadata.to_dict(),
        )

    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for SQL query including database type."""
        return sha256(
            f"{self._database_type.value}:{query}".encode("utf-8")
        ).hexdigest()[:16]
