"""Application settings and configuration management.

This module provides centralized configuration using immutable settings objects
that can be loaded from environment variables, CLI arguments, or config files.
"""

import os
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Literal

from domain.value_objects.database_type import DatabaseType


@dataclass(frozen=True)
class LLMSettings:
    """Settings for LLM provider configuration.

    Attributes:
        provider: LLM provider identifier
        model_name: Specific model to use (empty string uses provider default)
        temperature: Sampling temperature for generation (0.0-1.0)
        max_output_tokens: Maximum tokens to generate
        api_key: API key for authentication (None for providers that don't need it)
        timeout: Request timeout in seconds
    """

    provider: Literal["gemini", "openai", "claude", "oracle_genai"]
    model_name: str = ""
    temperature: float = 0.1
    max_output_tokens: int = 8192
    api_key: str | None = None
    timeout: int = 240

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if self.temperature < 0.0 or self.temperature > 1.0:
            raise ValueError(f"Temperature must be 0.0-1.0, got {self.temperature}")

        if self.max_output_tokens < 1:
            raise ValueError(
                f"max_output_tokens must be positive, got {self.max_output_tokens}"
            )

        if self.timeout < 1:
            raise ValueError(f"timeout must be positive, got {self.timeout}")


@dataclass(frozen=True)
class OracleGenAISettings:
    """Settings specific to Oracle GenAI provider.

    Attributes:
        compartment_id: OCI compartment identifier
        model_id: Oracle GenAI model identifier
        endpoint: API endpoint URL
        profile: OCI config profile name
        config_path: Path to OCI config file
    """

    compartment_id: str
    model_id: str
    endpoint: str
    profile: str = "DEFAULT"
    config_path: Path = field(default_factory=lambda: Path("infrastructure/oci/config"))

    def __post_init__(self) -> None:
        """Validate Oracle GenAI settings."""
        if not self.compartment_id:
            raise ValueError("compartment_id is required for Oracle GenAI")

        if not self.model_id:
            raise ValueError("model_id is required for Oracle GenAI")

        if not self.endpoint:
            raise ValueError("endpoint is required for Oracle GenAI")


@dataclass(frozen=True)
class StorageSettings:
    """Settings for file storage.

    Attributes:
        metadata_file: Path to metadata storage file
        create_dirs: Whether to create parent directories automatically
    """

    metadata_file: Path = Path("./optimization_metadata.json")
    create_dirs: bool = True


@dataclass(frozen=True)
class Settings:
    """Complete application settings.

    This immutable settings object provides all configuration needed
    by the application, infrastructure, and presentation layers.

    Attributes:
        llm: LLM provider settings
        database_type: Target database type for optimization
        storage: Storage configuration
        oracle_genai: Oracle GenAI specific settings (if applicable)
    """

    llm: LLMSettings
    database_type: DatabaseType
    storage: StorageSettings = field(default_factory=StorageSettings)
    oracle_genai: OracleGenAISettings | None = None

    @cached_property
    def effective_model_name(self) -> str:
        """Get the effective model name, using defaults if not specified.

        Returns:
            Model name to use for the configured provider
        """
        if self.llm.model_name:
            return self.llm.model_name

        # Provider defaults
        defaults = {
            "gemini": "gemini-2.0-flash-exp",
            "openai": "gpt-4",
            "claude": "claude-3-5-sonnet-20241022",
            "oracle_genai": self.oracle_genai.model_id
            if self.oracle_genai
            else "cohere.command-r-plus",
        }
        return defaults[self.llm.provider]

    @classmethod
    def from_env(cls, database_type: DatabaseType | None = None) -> "Settings":
        """Create settings from environment variables.

        Expected environment variables:
        - LLM_PROVIDER: Provider name (default: gemini)
        - LLM_MODEL: Model name (optional)
        - LLM_TEMPERATURE: Temperature (default: 0.1)
        - LLM_MAX_TOKENS: Max tokens (default: 8192)
        - GOOGLE_API_KEY: For Gemini
        - OPENAI_API_KEY: For OpenAI
        - ANTHROPIC_API_KEY: For Claude
        - OCI_COMPARTMENT_ID: For Oracle GenAI
        - OCI_MODEL_ID: For Oracle GenAI
        - OCI_GENAI_ENDPOINT: For Oracle GenAI
        - OCI_PROFILE: For Oracle GenAI (default: DEFAULT)
        - DATABASE_TYPE: Default database type (default: oracle)

        Args:
            database_type: Override database type (otherwise read from env)

        Returns:
            Settings instance configured from environment

        Examples:
            >>> settings = Settings.from_env()
            >>> settings.llm.provider
            'gemini'
        """
        provider = os.getenv("LLM_PROVIDER", "gemini")

        oracle_genai = None
        if provider == "oracle_genai":
            oracle_genai = OracleGenAISettings(
                compartment_id=os.getenv("OCI_COMPARTMENT_ID", ""),
                model_id=os.getenv("OCI_MODEL_ID", "cohere.command-r-plus"),
                endpoint=os.getenv(
                    "OCI_GENAI_ENDPOINT",
                    "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
                ),
                profile=os.getenv("OCI_PROFILE", "DEFAULT"),
            )
        return cls(
            llm=LLMSettings(
                provider=provider,  # type: ignore
                model_name=os.getenv("LLM_MODEL", ""),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
                max_output_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192")),
                api_key=cls._get_api_key_from_env(provider),
                timeout=int(os.getenv("LLM_TIMEOUT", "240")),
            ),
            database_type=database_type
            if database_type is not None
            else DatabaseType.from_string(os.getenv("DATABASE_TYPE", "oracle")),
            storage=StorageSettings(
                metadata_file=Path(
                    os.getenv("METADATA_FILE", "./optimization_metadata.json")
                ),
                create_dirs=os.getenv("CREATE_DIRS", "true").lower() == "true",
            ),
            oracle_genai=oracle_genai,
        )

    @classmethod
    def from_cli_args(
        cls,
        provider: str,
        database: str = "oracle",
        model: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> "Settings":
        """Create settings from CLI arguments.

        Args:
            provider: LLM provider name
            database: Database type
            model: Optional model name override
            api_key: Optional API key override
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            Settings instance configured from arguments

        Examples:
            >>> settings = Settings.from_cli_args(
            ...     provider="gemini",
            ...     database="oracle",
            ...     model="gemini-2.0-flash"
            ... )
        """
        # Get API key from argument or environment
        llm_settings = LLMSettings(
            provider=provider,  # type: ignore
            model_name=model or "",
            temperature=temperature,
            max_output_tokens=max_tokens,
            api_key=api_key or cls._get_api_key_from_env(provider),
        )
        # Oracle GenAI settings if applicable
        oracle_genai = None
        if provider == "oracle_genai":
            oracle_genai = OracleGenAISettings(
                compartment_id=os.getenv("OCI_COMPARTMENT_ID", ""),
                model_id=model or os.getenv("OCI_MODEL_ID", "cohere.command-r-plus"),
                endpoint=os.getenv(
                    "OCI_GENAI_ENDPOINT",
                    "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
                ),
                profile=os.getenv("OCI_PROFILE", "DEFAULT"),
            )
        return cls(
            llm=llm_settings,
            database_type=DatabaseType.from_string(database),
            storage=StorageSettings(),
            oracle_genai=oracle_genai,
        )

    @staticmethod
    def _get_api_key_from_env(provider: str) -> str | None:
        """Get API key from environment for the specified provider.

        Args:
            provider: LLM provider name

        Returns:
            API key if found, None otherwise
        """
        if env_var := {
            "gemini": "GOOGLE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }.get(provider):
            return os.getenv(env_var)

        return None
