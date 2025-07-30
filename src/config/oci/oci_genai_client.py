# src/config/oci/oci_genai_client.py

import os
from typing import Any, LiteralString

import oci

from config.logger import logger


class OCIOracleGenAIClient:
    """Wrapper for Oracle Generative AI using OCI SDK."""

    def __init__(
        self,
        config_profile: str,
        compartment_id: str,
        model_id: str,
        endpoint: str,
    ):
        self.compartment_id = compartment_id
        self.model_id = model_id

        config_path: LiteralString = os.path.join("src", "config", "oci", "config")
        self.oci_config = oci.config.from_file(config_path, config_profile)
        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=self.oci_config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240),
        )

    def generate_chat_response(self, prompt: str, parameters: dict[str, Any]) -> str:
        """Send a chat request to Oracle GenAI and return the model response."""

        try:
            chat_detail = oci.generative_ai_inference.models.ChatDetails()
            chat_request = oci.generative_ai_inference.models.CohereChatRequest()

            chat_request.message = prompt
            chat_request.max_tokens = parameters.get("max_output_tokens", 600)
            chat_request.temperature = parameters.get("temperature", 1)
            chat_request.frequency_penalty = parameters.get("frequency_penalty", 0)
            chat_request.top_p = parameters.get("top_p", 0.75)
            chat_request.top_k = parameters.get("top_k", 0)

            chat_detail.serving_mode = (
                oci.generative_ai_inference.models.OnDemandServingMode(
                    model_id=self.model_id
                )
            )
            chat_detail.chat_request = chat_request
            chat_detail.compartment_id = self.compartment_id

            logger.info("Sending prompt to Oracle GenAI...")
            return self.client.chat(chat_detail).data.chat_response.text.strip()

        except Exception as e:
            logger.error(f"Oracle GenAI chat failed: {str(e)}")
            raise e
