"""Anthropic Claude LLM adapter implementation."""

from anthropic import Anthropic, APIError

from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.llm.base_adapter import BaseLLMAdapter


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude LLM provider.

    This adapter implements the LLMPort interface for Anthropic's Claude models.

    Attributes:
        _client: Configured Anthropic client instance

    Examples:
        >>> from anthropic import Anthropic
        >>> adapter = AnthropicAdapter(
        ...     Anthropic(api_key="your-api-key"),
        ...     "claude-3-5-sonnet-20241022"
        ... )
        >>> response = await adapter.generate_text("Explain this SQL query...")
    """

    def __init__(self, client: Anthropic, model_name: str) -> None:
        """Initialize Anthropic adapter.

        Args:
            client: Configured Anthropic client
            model_name: Claude model identifier
        """
        super().__init__(model_name)
        self._client = client

    async def generate_text(
        self, prompt: str, temperature: float = 0.1, max_tokens: int = 8192
    ) -> str:
        """Generate text using Anthropic Claude.

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
            response = self._client.messages.create(
                model=self._model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            if not response.content:  # Claude returns a list of content blocks
                raise LLMProviderError("Claude returned no content blocks")

            self._log_response(
                result := self._validate_response(response.content[0].text)  # type: ignore
            )
            return result

        except APIError as e:
            self._log_error(e)
            raise LLMProviderError(f"Anthropic API error: {e}") from e
        except Exception as e:
            self._log_error(e)
            raise LLMProviderError(f"Unexpected Anthropic error: {e}") from e

    @property
    def provider_name(self) -> str:
        """Get provider identifier.

        Returns:
            Provider name string
        """
        return "claude"
