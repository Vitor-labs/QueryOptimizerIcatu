# src/config/config.py
from dataclasses import dataclass, field
from typing import Literal

from core.types import DatabaseType


@dataclass
class OptimizerConfig:
    """Configuration for query optimizer."""

    provider: Literal["gemini", "openai", "claude", "oracle_genai"] = "gemini"
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.1
    max_output_tokens: int = 8192
    database_type: DatabaseType = DatabaseType.ORACLE
    # API Keys (optional, for Gemini, OpenAI, Claude. Can be set via environment variables)
    api_key: str | None = None
    # Extra parameters for OCI Oracle GenAI
    extra: dict[str, str] = field(default_factory=dict)

    def get_default_model_for_provider(self) -> str:
        """Get default model name for the provider."""
        return {
            "gemini": "gemini-2.0-flash",
            "openai": "gpt-4",
            "claude": "claude-3-5-sonnet-20241022",
            "oracle_genai": self.extra.get("model_id", "cohere.command"),
        }.get(self.provider, self.model_name)

    def __post_init__(self) -> None:
        """Post-initialization to set default model if not specified."""
        if self.model_name == "gemini-2.0-flash" and self.provider != "gemini":
            self.model_name = self.get_default_model_for_provider()
