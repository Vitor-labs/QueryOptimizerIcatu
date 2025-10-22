"""Use case for comparing optimizations across multiple databases.

This module implements the business logic for optimizing the same SQL query
for multiple database systems and comparing the results.
"""

from pathlib import Path

from application.dto.optimization_dto import ComparisonDTO, OptimizationDTO
from application.ports.llm_port import LLMPort
from application.ports.storage_port import FileStoragePort, MetadataRepositoryPort
from application.use_cases.optimize_query import OptimizeQueryUseCase
from domain.exceptions.domain_exceptions import OptimizationError
from domain.value_objects.database_type import DatabaseType


class CompareOptimizationsUseCase:
    """Use case for comparing query optimizations across databases.

    This use case optimizes the same SQL query for multiple database types
    and returns a comparison of the results.

    Attributes:
        _llm: LLM provider adapter
        _storage: File storage adapter
        _metadata_repo: Metadata repository
        _prompt_generator_factory: Factory for creating prompt generators

    Examples:
        >>> use_case = CompareOptimizationsUseCase(
        ...     llm_adapter=gemini_adapter,
        ...     file_handler=local_storage,
        ...     metadata_repository=json_repo,
        ...     prompt_generator_factory=PromptGeneratorFactory(),
        ... )
        >>> comparison = await use_case.execute(
        ...     Path("query.sql"),
        ...     [DatabaseType.ORACLE, DatabaseType.SQLITE]
        ... )
    """

    def __init__(
        self,
        llm_adapter: LLMPort,
        file_handler: FileStoragePort,
        metadata_repository: MetadataRepositoryPort,
        prompt_generator_factory: type,  # Factory class for prompt generators
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            llm_adapter: LLM provider for text generation
            file_handler: Storage for reading SQL and writing results
            metadata_repository: Repository for optimization metadata
            prompt_generator_factory: Factory for creating prompt generators
        """
        self._llm = llm_adapter
        self._storage = file_handler
        self._metadata_repo = metadata_repository
        self._prompt_factory = prompt_generator_factory

    async def execute(
        self,
        sql_file: Path,
        database_types: list[DatabaseType] | None = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> ComparisonDTO:
        """Execute optimization comparison across database types.

        Args:
            sql_file: Path to SQL file to optimize
            database_types: List of database types to compare (defaults to all supported)
            temperature: LLM temperature parameter (0.0-1.0)
            max_tokens: Maximum tokens for LLM generation

        Returns:
            DTO containing comparison results for all database types

        Raises:
            FileNotFoundError: If SQL file doesn't exist
            OptimizationError: If any optimization fails

        Examples:
            >>> comparison = await use_case.execute(
            ...     Path("query.sql"),
            ...     [DatabaseType.ORACLE, DatabaseType.SQLITE, DatabaseType.SQLSERVER]
            ... )
            >>> for db_type in comparison.database_types():
            ...     opt = comparison.get_optimization(DatabaseType(db_type))
            ...     print(f"{db_type}: {opt.version}")
        """
        # Validate file exists
        if not await self._storage.exists(sql_file):
            raise FileNotFoundError(f"SQL file not found: {sql_file}")

        # Read original query
        original_query = await self._storage.read_text(sql_file)

        # Use all supported database types if none specified
        if database_types is None:
            database_types = list(DatabaseType)

        # Optimize for each database type
        optimizations: dict[str, OptimizationDTO] = {}
        errors: dict[str, Exception] = {}

        for db_type in database_types:
            try:
                optimizations[db_type.value] = await self._optimize_for_database(
                    sql_file, db_type, temperature, max_tokens
                )
            except Exception as e:  # Collect errors but continue with other databases
                errors[db_type.value] = e

        if not optimizations:  # If all optimizations failed, raise error
            raise OptimizationError(
                f"All optimizations failed:\n{'\n'.join(f'{db}: {err}' for db, err in errors.items())}"
            )
        # Save comparison results
        await self._save_comparison_file(sql_file, original_query, optimizations)
        return ComparisonDTO(
            original_query=original_query,
            optimizations=optimizations,
        )

    async def _optimize_for_database(
        self,
        sql_file: Path,
        database_type: DatabaseType,
        temperature: float,
        max_tokens: int,
    ) -> OptimizationDTO:
        """Optimize query for a specific database type.

        Args:
            sql_file: SQL file to optimize
            database_type: Target database type
            temperature: LLM temperature
            max_tokens: Maximum tokens

        Returns:
            Optimization result DTO
        """
        # Create prompt generator for this database type
        # Create and execute optimization use case
        return await OptimizeQueryUseCase(
            llm_adapter=self._llm,
            file_handler=self._storage,
            metadata_repository=self._metadata_repo,
            prompt_generator=self._prompt_factory.create(database_type),
        ).execute(
            sql_file,
            database_type,
            temperature,
            max_tokens,
        )

    async def _save_comparison_file(
        self,
        sql_file: Path,
        original_query: str,
        optimizations: dict[str, OptimizationDTO],
    ) -> None:
        """Save comparison results to JSON file.

        Args:
            sql_file: Original SQL file path
            original_query: Original SQL query text
            optimizations: Map of database type to optimization results
        """
        await self._storage.write_json(
            sql_file.with_name(f"{sql_file.stem}_comparison.json"),
            {
                "original_query": original_query,
                "databases": {
                    db_type: opt.to_dict() for db_type, opt in optimizations.items()
                },  # type: ignore
            },
        )
