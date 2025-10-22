"""Oracle GenAI LLM adapter implementation."""

from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.config.settings import OracleGenAISettings
from infrastructure.llm.base_adapter import BaseLLMAdapter
from infrastructure.oci.oci_client import OCIGenAIClient


class OracleGenAIAdapter(BaseLLMAdapter):
    """Adapter for Oracle Generative AI provider.

    This adapter implements the LLMPort interface for Oracle's GenAI service.

    Attributes:
        _client: OCI GenAI client wrapper

    Examples:
        >>> adapter = OracleGenAIAdapter.from_settings(oracle_genai_settings)
        >>> response = await adapter.generate_text("Explain this SQL query...")
    """

    def __init__(self, client: OCIGenAIClient, model_name: str) -> None:
        """Initialize Oracle GenAI adapter.

        Args:
            client: Configured OCI GenAI client
            model_name: Model identifier
        """
        super().__init__(model_name)
        self._client = client

    @classmethod
    def from_settings(cls, settings: OracleGenAISettings) -> "OracleGenAIAdapter":
        """Create adapter from settings.

        Args:
            settings: Oracle GenAI configuration settings

        Returns:
            Configured adapter instance
        """
        return cls(
            OCIGenAIClient(
                config_profile=settings.profile,
                config_path=settings.config_path,
                compartment_id=settings.compartment_id,
                model_id=settings.model_id,
                endpoint=settings.endpoint,
            ),
            settings.model_id,
        )

    async def generate_text(
        self, prompt: str, temperature: float = 0.1, max_tokens: int = 8192
    ) -> str:
        """Generate text using Oracle GenAI.

        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If generation fails
        """
        self._log_request(prompt, temperature=temperature, max_tokens=max_tokens)
        try:
            self._log_response(
                validated := self._validate_response(
                    self._client.generate_chat_response(
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                )
            )
            return validated

        except LLMProviderError:
            raise
        except Exception as e:
            self._log_error(e)
            raise LLMProviderError(f"Oracle GenAI error: {e}") from e

    @property
    def provider_name(self) -> str:
        """Get provider identifier.

        Returns:
            Provider name string
        """
        return "oracle_genai"
