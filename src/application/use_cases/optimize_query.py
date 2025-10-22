"""Use case for optimizing a single SQL query.

This module implements the core business logic for optimizing a SQL query
using LLM-based transformation: SQL → Natural Language → Optimized SQL.
"""

from pathlib import Path

from application.dto.optimization_dto import OptimizationDTO
from application.ports.llm_port import LLMPort
from application.ports.prompt_port import PromptGeneratorPort
from application.ports.storage_port import FileStoragePort, MetadataRepositoryPort
from domain.entities.optimization import OptimizationMetadata, OptimizationResult
from domain.exceptions.domain_exceptions import OptimizationError, QueryValidationError
from domain.value_objects.database_type import DatabaseType
from domain.value_objects.query_hash import QueryHash


class OptimizeQueryUseCase:
    """Use case for optimizing a SQL query for a specific database.

    This use case orchestrates the optimization process:
    1. Read SQL query from file
    2. Convert SQL to natural language explanation
    3. Convert explanation back to optimized SQL
    4. Save results and metadata

    Attributes:
        _llm: LLM provider adapter
        _storage: File storage adapter
        _metadata_repo: Metadata persistence adapter
        _prompt_generator: Prompt generator for target database

    Examples:
        >>> use_case = OptimizeQueryUseCase(
        ...     llm_adapter=gemini_adapter,
        ...     file_handler=local_storage,
        ...     metadata_repository=json_repo,
        ...     prompt_generator=oracle_generator,
        ... )
        >>> result = await use_case.execute(
        ...     Path("query.sql"),
        ...     DatabaseType.ORACLE
        ... )
    """

    def __init__(
        self,
        llm_adapter: LLMPort,
        file_handler: FileStoragePort,
        metadata_repository: MetadataRepositoryPort,
        prompt_generator: PromptGeneratorPort,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            llm_adapter: LLM provider for text generation
            file_handler: Storage for reading SQL and writing results
            metadata_repository: Repository for optimization metadata
            prompt_generator: Generator for database-specific prompts
        """
        self._llm = llm_adapter
        self._storage = file_handler
        self._metadata_repo = metadata_repository
        self._prompt_generator = prompt_generator

    async def execute(
        self,
        sql_file: Path,
        database_type: DatabaseType,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> OptimizationDTO:
        """Execute query optimization process.

        Args:
            sql_file: Path to SQL file to optimize
            database_type: Target database system
            temperature: LLM temperature parameter (0.0-1.0)
            max_tokens: Maximum tokens for LLM generation

        Returns:
            DTO containing optimization results

        Raises:
            FileNotFoundError: If SQL file doesn't exist
            QueryValidationError: If query is invalid
            OptimizationError: If optimization process fails

        Examples:
            >>> result = await use_case.execute(
            ...     Path("complex_query.sql"),
            ...     DatabaseType.ORACLE,
            ...     temperature=0.1,
            ...     max_tokens=4000
            ... )
            >>> print(f"Optimized version: {result.version}")
        """
        if not await self._storage.exists(sql_file):  # Validate inputs
            raise FileNotFoundError(f"SQL file not found: {sql_file}")

        if self._prompt_generator.get_database_type() != database_type:
            raise ValueError(
                f"Prompt generator is for {self._prompt_generator.get_database_type()}, "
                f"but requested {database_type}"
            )
        # Read original query
        if not self._prompt_generator.validate_query(
            original_query := await self._storage.read_text(sql_file)
        ):
            raise QueryValidationError(f"Invalid SQL query in {sql_file}")

        metadata = await self._get_or_create_metadata(
            QueryHash.from_query(original_query, database_type),
            original_query,
            database_type,
        )
        try:  # Step 1: SQL → Natural Language
            explanation = await self._convert_sql_to_natural(
                original_query, temperature, max_tokens
            )
            # Step 2: Natural Language → Optimized SQL
            optimized_query = await self._convert_natural_to_sql(
                explanation, temperature, max_tokens
            )
            metadata.explanation = explanation
            metadata.increment_version()

            result = OptimizationResult(
                metadata=metadata, optimized_query=optimized_query
            )
            # Persist metadata and output file and return
            await self._metadata_repo.save(metadata)
            await self._save_output_file(sql_file, result)
            return OptimizationDTO.from_result(result)

        except Exception as e:
            raise OptimizationError(f"Optimization failed: {e}") from e

    async def _convert_sql_to_natural(
        self, query: str, temperature: float, max_tokens: int
    ) -> str:
        """Convert SQL query to natural language explanation.

        Args:
            query: SQL query text
            temperature: LLM temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Natural language explanation of the query
        """
        return await self._llm.generate_text(
            self._prompt_generator.sql_to_natural(query), temperature, max_tokens
        )

    async def _convert_natural_to_sql(
        self, explanation: str, temperature: float, max_tokens: int
    ) -> str:
        """Convert natural language explanation to optimized SQL.

        Args:
            explanation: Natural language description
            temperature: LLM temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Optimized SQL query
        """
        return await self._llm.generate_text(
            self._prompt_generator.natural_to_sql(explanation), temperature, max_tokens
        )

    async def _get_or_create_metadata(
        self, query_hash: QueryHash, query: str, database_type: DatabaseType
    ) -> OptimizationMetadata:
        """Get existing metadata or create new entry.

        Args:
            query_hash: Hash of the query
            query: SQL query text
            database_type: Target database type

        Returns:
            Existing or new metadata instance
        """
        if existing := await self._metadata_repo.get(query_hash):
            return existing

        return OptimizationMetadata.create_new(query, database_type)

    async def _save_output_file(
        self, sql_file: Path, result: OptimizationResult
    ) -> None:
        """Save optimization results to JSON file.

        Args:
            sql_file: Original SQL file path (used to determine output path)
            result: Optimization result to save
        """
        await self._storage.write_json(
            sql_file.with_name(
                f"{sql_file.stem}_{result.database_type.value}_optimization.json"
            ),
            result.to_dict(),  # type: ignore
        )
