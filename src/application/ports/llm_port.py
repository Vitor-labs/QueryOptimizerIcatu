"""Port (interface) for LLM providers.

This port defines the contract that any LLM provider adapter must implement.
It abstracts away the specific LLM implementation details from the use cases.
"""

from abc import ABC, abstractmethod

from domain.exceptions.domain_exceptions import LLMProviderError


class LLMPort(ABC):
    """Abstract interface for LLM text generation providers.

    This port enables the application layer to work with any LLM provider
    without coupling to specific implementations. Adapters in the infrastructure
    layer implement this interface for concrete providers (Gemini, OpenAI, etc.).

    Examples:
        >>> class MyLLMAdapter(LLMPort):
        ...     async def generate_text(self, prompt: str, **kwargs) -> str:
        ...         # Implementation here
        ...         return "Generated text"
        ...
        ...     @property
        ...     def provider_name(self) -> str:
        ...         return "my-provider"
    """

    @abstractmethod
    async def generate_text(
        self, prompt: str, temperature: float = 0.1, max_tokens: int = 8192
    ) -> str:
        """Generate text response from the LLM.

        Args:
            prompt: Input prompt text to send to the LLM
            temperature: Sampling temperature (0.0-1.0). Lower is more deterministic.
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response from the LLM

        Raises:
            LLMProviderError: If text generation fails for any reason

        Examples:
            >>> adapter = get_llm_adapter()
            >>> response = await adapter.generate_text(
            ...     "Explain this SQL: SELECT * FROM users",
            ...     temperature=0.1,
            ...     max_tokens=1000
            ... )
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the LLM provider identifier.

        Returns:
            Provider name (e.g., "gemini", "openai", "claude")

        Examples:
            >>> adapter = get_llm_adapter()
            >>> adapter.provider_name
            'gemini'
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the specific model being used.

        Returns:
            Model identifier (e.g., "gpt-4", "gemini-2.0-flash")

        Examples:
            >>> adapter = get_llm_adapter()
            >>> adapter.model_name
            'gemini-2.0-flash'
        """

    async def health_check(self) -> bool:
        """Check if the LLM provider is available and responsive.

        This is an optional method that can be overridden by implementations
        to provide health checking capabilities.

        Returns:
            True if provider is healthy, False otherwise

        Examples:
            >>> adapter = get_llm_adapter()
            >>> is_healthy = await adapter.health_check()
            >>> if is_healthy:
            ...     print("Provider is ready")
        """
        try:  # Simple health check: try to generate minimal text
            await self.generate_text("test", temperature=0.0, max_tokens=1)
            return True
        except LLMProviderError:
            return False
