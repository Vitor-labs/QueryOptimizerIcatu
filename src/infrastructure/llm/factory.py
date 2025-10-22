"""Factory for creating LLM adapters from settings."""

from anthropic import Anthropic
from google.genai import Client as GeminiClient
from openai import OpenAI

from application.ports.llm_port import LLMPort
from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.config.logger import get_logger
from infrastructure.config.settings import Settings
from infrastructure.llm.anthropic_adapter import AnthropicAdapter
from infrastructure.llm.gemini_adapter import GeminiAdapter
from infrastructure.llm.openai_adapter import OpenAIAdapter
from infrastructure.llm.oracle_genai_adapter import OracleGenAIAdapter

logger = get_logger(__name__)


class LLMAdapterFactory:
    """Factory for creating LLM provider adapters.

    This factory creates concrete adapter implementations based on
    application settings, handling provider-specific initialization.

    Examples:
        >>> settings = Settings.from_env()
        >>> adapter = LLMAdapterFactory.create(settings)
        >>> response = await adapter.generate_text("prompt")
    """

    @staticmethod
    def create(settings: Settings) -> LLMPort:
        """Create LLM adapter from settings.

        Args:
            settings: Application settings with LLM configuration

        Returns:
            Configured LLM adapter implementation

        Raises:
            LLMProviderError: If provider is unsupported or configuration is invalid
        """
        provider = settings.llm.provider
        model = settings.effective_model_name

        logger.info("Creating LLM adapter", provider=provider, model=model)

        try:
            if provider == "gemini":
                return LLMAdapterFactory._create_gemini(settings, model)

            if provider == "openai":
                return LLMAdapterFactory._create_openai(settings, model)

            if provider == "claude":
                return LLMAdapterFactory._create_claude(settings, model)

            if provider == "oracle_genai":
                return LLMAdapterFactory._create_oracle_genai(settings)

            raise LLMProviderError(f"Unsupported LLM provider: {provider}")

        except LLMProviderError:
            raise
        except Exception as e:
            logger.error(
                "Failed to create LLM adapter", provider=provider, error=str(e)
            )
            raise LLMProviderError(f"Failed to create {provider} adapter: {e}") from e

    @staticmethod
    def _create_gemini(settings: Settings, model: str) -> GeminiAdapter:
        """Create Gemini adapter.

        Args:
            settings: Application settings
            model: Model name

        Returns:
            Configured Gemini adapter
        """
        if not settings.llm.api_key:
            raise LLMProviderError("Gemini requires API key (GOOGLE_API_KEY)")
        return GeminiAdapter(GeminiClient(api_key=settings.llm.api_key), model)

    @staticmethod
    def _create_openai(settings: Settings, model: str) -> OpenAIAdapter:
        """Create OpenAI adapter.

        Args:
            settings: Application settings
            model: Model name

        Returns:
            Configured OpenAI adapter
        """
        if not settings.llm.api_key:
            raise LLMProviderError("OpenAI requires API key (OPENAI_API_KEY)")

        return OpenAIAdapter(OpenAI(api_key=settings.llm.api_key), model)

    @staticmethod
    def _create_claude(settings: Settings, model: str) -> AnthropicAdapter:
        """Create Anthropic adapter.

        Args:
            settings: Application settings
            model: Model name

        Returns:
            Configured Anthropic adapter
        """
        if not settings.llm.api_key:
            raise LLMProviderError("Claude requires API key (ANTHROPIC_API_KEY)")

        return AnthropicAdapter(Anthropic(api_key=settings.llm.api_key), model)

    @staticmethod
    def _create_oracle_genai(settings: Settings) -> OracleGenAIAdapter:
        """Create Oracle GenAI adapter.

        Args:
            settings: Application settings

        Returns:
            Configured Oracle GenAI adapter
        """
        if not settings.oracle_genai:
            raise LLMProviderError("Oracle GenAI requires OracleGenAISettings")

        return OracleGenAIAdapter.from_settings(settings.oracle_genai)
