"""Base adapter for LLM providers.

This module provides a base class with common functionality for all LLM adapters.
"""

from abc import ABC
from typing import Any

from application.ports.llm_port import LLMPort
from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.config.logger import get_logger

logger = get_logger(__name__)


class BaseLLMAdapter(LLMPort, ABC):
    """Base class for LLM adapter implementations.

    Provides common functionality like logging, error handling,
    and response validation that all adapters can use.

    Attributes:
        _model_name: The specific model identifier
    """

    def __init__(self, model_name: str) -> None:
        """Initialize base adapter.

        Args:
            model_name: Model identifier to use
        """
        self._model_name = model_name
        logger.info(
            "LLM adapter initialized",
            provider=self.provider_name,
            model=model_name,
        )

    @property
    def model_name(self) -> str:
        """Get the model name.

        Returns:
            Model identifier string
        """
        return self._model_name

    def _validate_response(self, response: str | None) -> str:
        """Validate LLM response is not empty.

        Args:
            response: Response text from LLM

        Returns:
            Validated response text

        Raises:
            LLMProviderError: If response is empty or None
        """
        if not response or not response.strip():
            raise LLMProviderError(f"{self.provider_name} returned empty response")
        return response.strip()

    def _log_request(self, prompt: str, **kwargs: Any) -> None:
        """Log LLM request details.

        Args:
            prompt: Prompt being sent
            **kwargs: Additional parameters
        """
        logger.debug(
            "LLM request",
            provider=self.provider_name,
            model=self._model_name,
            prompt_length=len(prompt),
            **kwargs,
        )

    def _log_response(self, response: str, **kwargs: Any) -> None:
        """Log LLM response details.

        Args:
            response: Response received
            **kwargs: Additional metadata
        """
        logger.debug(
            "LLM response",
            provider=self.provider_name,
            model=self._model_name,
            response_length=len(response),
            **kwargs,
        )

    def _log_error(self, error: Exception, **kwargs: Any) -> None:
        """Log LLM error.

        Args:
            error: Exception that occurred
            **kwargs: Additional context
        """
        logger.error(
            "LLM request failed",
            provider=self.provider_name,
            model=self._model_name,
            error=str(error),
            error_type=type(error).__name__,
            **kwargs,
        )
