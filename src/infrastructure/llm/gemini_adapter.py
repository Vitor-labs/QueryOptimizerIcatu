"""Google Gemini LLM adapter implementation."""

from google.genai import Client as GeminiClient
from google.genai.errors import ClientError

from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.llm.base_adapter import BaseLLMAdapter


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini LLM provider.

    This adapter implements the LLMPort interface for Google's Gemini models.

    Attributes:
        _client: Configured Gemini client instance

    Examples:
        >>> from google.genai import Client
        >>> adapter = GeminiAdapter(
        ...     Client(api_key="your-api-key"),
        ...     "gemini-2.0-flash-exp"
        ... )
        >>> response = await adapter.generate_text("Explain this SQL query...")
    """

    def __init__(self, client: GeminiClient, model_name: str) -> None:
        """Initialize Gemini adapter.

        Args:
            client: Configured Google Gemini client
            model_name: Gemini model identifier (e.g., "gemini-2.0-flash-exp")
        """
        super().__init__(model_name)
        self._client = client

    async def generate_text(
        self, prompt: str, temperature: float = 0.1, max_tokens: int = 8192
    ) -> str:
        """Generate text using Google Gemini.

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
                self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                ).text
            )
            self._log_response(result)
            return result

        except ClientError as e:
            self._log_error(e)
            raise LLMProviderError(f"Gemini API error: {e}") from e
        except Exception as e:
            self._log_error(e)
            raise LLMProviderError(f"Unexpected Gemini error: {e}") from e

    @property
    def provider_name(self) -> str:
        """Get provider identifier.

        Returns:
            Provider name string
        """
        return "gemini"
