"""OpenAI LLM adapter implementation."""

from openai import OpenAI, OpenAIError

from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.llm.base_adapter import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI LLM provider.

    This adapter implements the LLMPort interface for OpenAI's GPT models.

    Attributes:
        _client: Configured OpenAI client instance

    Examples:
        >>> from openai import OpenAI
        >>> adapter = OpenAIAdapter(
        ...     OpenAI(api_key="your-api-key"),
        ...     "gpt-4"
        ... )
        >>> response = await adapter.generate_text("Explain this SQL query...")
    """

    def __init__(self, client: OpenAI, model_name: str) -> None:
        """Initialize OpenAI adapter.

        Args:
            client: Configured OpenAI client
            model_name: OpenAI model identifier (e.g., "gpt-4", "gpt-4-turbo")
        """
        super().__init__(model_name)
        self._client = client

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> str:
        """Generate text using OpenAI.

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
            result = self._validate_response(
                self._client.chat.completions.create(
                    model=self._model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                .choices[0]
                .message.content
            )
            self._log_response(result)
            return result

        except OpenAIError as e:
            self._log_error(e)
            raise LLMProviderError(f"OpenAI API error: {e}") from e
        except Exception as e:
            self._log_error(e)
            raise LLMProviderError(f"Unexpected OpenAI error: {e}") from e

    @property
    def provider_name(self) -> str:
        """Get provider identifier.

        Returns:
            Provider name string
        """
        return "openai"
