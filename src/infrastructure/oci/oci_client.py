"""Oracle Cloud Infrastructure GenAI client wrapper.

This module provides a wrapper around the OCI SDK for interacting
with Oracle's Generative AI service.
"""

import re
from pathlib import Path

import oci
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    ChatDetails,
    CohereChatRequest,
    OnDemandServingMode,
)

from domain.exceptions.domain_exceptions import LLMProviderError
from infrastructure.config.logger import get_logger

logger = get_logger(__name__)


class OCIGenAIClient:
    """Wrapper for Oracle Generative AI using OCI SDK.

    This client handles authentication and request formatting for
    Oracle's GenAI service using the OCI SDK.

    Attributes:
        _compartment_id: OCI compartment identifier
        _model_id: Model identifier to use
        _client: OCI GenAI client instance
    """

    def __init__(
        self,
        config_profile: str,
        config_path: Path,
        compartment_id: str,
        model_id: str,
        endpoint: str,
    ) -> None:
        """Initialize OCI GenAI client.

        Args:
            config_profile: OCI config profile name (e.g., "DEFAULT")
            config_path: Path to OCI config file
            compartment_id: OCI compartment ID
            model_id: GenAI model ID
            endpoint: GenAI service endpoint URL
        """
        self._compartment_id = compartment_id
        self._model_id = model_id

        # Load OCI configuration
        try:
            self._oci_config = oci.config.from_file(
                str(config_path),
                config_profile,
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to load OCI config: {e}") from e

        try:
            self._client = GenerativeAiInferenceClient(
                config=self._oci_config,
                service_endpoint=endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10, 240),
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize OCI GenAI client: {e}") from e

        logger.info(
            "OCI GenAI client initialized",
            compartment_id=compartment_id,
            model_id=model_id,
            endpoint=endpoint,
        )

    def generate_chat_response(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4000,
        top_p: float = 0.75,
        top_k: int = 0,
        frequency_penalty: float = 0.0,
    ) -> str:
        """Generate chat response from Oracle GenAI.

        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            frequency_penalty: Frequency penalty parameter

        Returns:
            Generated text response (cleaned of markdown)

        Raises:
            LLMProviderError: If generation fails
        """
        try:
            chat_request = CohereChatRequest()
            chat_request.message = prompt
            chat_request.max_tokens = max_tokens
            chat_request.temperature = temperature
            chat_request.top_p = top_p
            chat_request.top_k = top_k
            chat_request.frequency_penalty = frequency_penalty

            chat_detail = ChatDetails()
            chat_detail.serving_mode = OnDemandServingMode(model_id=self._model_id)
            chat_detail.chat_request = chat_request
            chat_detail.compartment_id = self._compartment_id

            # Send request and Extract and clean response
            logger.debug("Sending request to Oracle GenAI", prompt_length=len(prompt))
            cleaned_text = self._clean_response(
                self._client.chat(chat_detail).data.chat_response.text.strip()  # type: ignore
            )
            logger.debug(
                "Received response from Oracle GenAI", response_length=len(cleaned_text)
            )
            return cleaned_text

        except Exception as e:
            logger.error("Oracle GenAI request failed", error=str(e))
            raise LLMProviderError(f"Oracle GenAI error: {e}") from e

    def _clean_response(self, response: str) -> str:
        """Clean response by removing markdown code blocks.

        Oracle GenAI sometimes wraps SQL in ```sql...``` blocks.
        This method removes those markers.

        Args:
            response: Raw response text

        Returns:
            Cleaned response text
        """
        return re.sub(  # Remove SQL markdown blocks
            r"^```sql\s*|```$",
            "",
            response.strip(),
            flags=re.IGNORECASE | re.MULTILINE,
        ).strip()
