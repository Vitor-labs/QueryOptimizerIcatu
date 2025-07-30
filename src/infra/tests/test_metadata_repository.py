# tests/test_metadata_repository.py
import pytest

from core.types import DatabaseType, QueryMetadata
from infra.metadata_repository import JsonMetadataRepository


class TestJsonMetadataRepository:
    """Test JsonMetadataRepository functionality."""

    @pytest.fixture
    def metadata_repo(self, temp_json_file) -> JsonMetadataRepository:
        """Create metadata repository instance."""
        return JsonMetadataRepository(temp_json_file)

    @pytest.mark.asyncio
    async def test_save_and_get_metadata(
        self, metadata_repo: JsonMetadataRepository, sample_metadata: QueryMetadata
    ):
        """Test saving and retrieving metadata."""
        query_hash = "test_hash_123"

        await metadata_repo.save_metadata(query_hash, sample_metadata)
        retrieved = await metadata_repo.get_metadata(query_hash)

        assert retrieved is not None
        assert retrieved.query_sql == sample_metadata.query_sql
        assert retrieved.explanation_text == sample_metadata.explanation_text
        assert retrieved.version == sample_metadata.version
        assert retrieved.database_type == sample_metadata.database_type

    @pytest.mark.asyncio
    async def test_get_nonexistent_metadata(
        self, metadata_repo: JsonMetadataRepository
    ):
        """Test retrieving non-existent metadata."""
        assert (await metadata_repo.get_metadata("nonexistent_hash")) is None

    def test_generate_hash_for_query(self, metadata_repo: JsonMetadataRepository):
        """Test query hash generation."""
        query = "SELECT * FROM users;"
        db_type = DatabaseType.ORACLE

        hash1 = metadata_repo.generate_hash_for_query(query, db_type)
        # Same query should generate same hash
        assert hash1 == metadata_repo.generate_hash_for_query(query, db_type)

        # Different database type should generate different hash
        assert hash1 != metadata_repo.generate_hash_for_query(
            query, DatabaseType.SQLITE
        )
