# src/llm/clients.py
import os
from typing import Any

from anthropic import Anthropic
from google.genai import Client as GeminiClient
from openai import OpenAI

from config.config import OptimizerConfig
from config.logger import logger
from core.interfaces import LLMClient


class GeminiLLMClient(LLMClient):
    """Google Gemini LLM client implementation."""

    def __init__(self, client: GeminiClient) -> None:
        self._client = client

    async def generate_response(self, prompt: str, config: dict[str, Any]) -> str:
        """Generate response using Gemini."""
        try:
            response = self._client.models.generate_content(
                model=config.get("model_name", "gemini-2.0-flash"),
                contents=prompt,
                config={
                    "temperature": config.get("temperature", 0.1),
                    "max_output_tokens": config.get("max_output_tokens", 8192),
                },
            ).text

            return response if response else "No response from the AI model"

        except Exception as e:
            error_msg = f"Error generating Gemini response: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"


class OpenAILLMClient(LLMClient):
    """OpenAI LLM client implementation."""

    def __init__(self, client: OpenAI) -> None:
        self._client = client

    async def generate_response(self, prompt: str, config: dict[str, Any]) -> str:
        """Generate response using OpenAI."""
        try:
            response = self._client.chat.completions.create(
                model=config.get("model_name", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_output_tokens", 8192),
            )
            return (
                response.choices[0].message.content or "No response from the AI model"
            )
        except Exception as e:
            error_msg = f"Error generating OpenAI response: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "openai"


class AnthropicLLMClient(LLMClient):
    """Anthropic Claude LLM client implementation."""

    def __init__(self, client: Anthropic) -> None:
        self._client = client

    async def generate_response(self, prompt: str, config: dict[str, Any]) -> str:
        """Generate response using Anthropic Claude."""
        try:
            response = self._client.messages.create(
                model=config.get("model_name", "claude-3-5-sonnet-20241022"),
                max_tokens=config.get("max_output_tokens", 8192),
                temperature=config.get("temperature", 0.1),
                messages=[{"role": "user", "content": prompt}],
            ).content

            return response[0].text if response else "No response from the AI model"

        except Exception as e:
            error_msg = f"Error generating Anthropic response: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "claude"


class LLMClientFactory:
    """Factory for creating LLM clients."""

    @staticmethod
    def create_client(config: OptimizerConfig, api_key: str | None = None) -> LLMClient:
        """Create an LLM client based on the configuration."""
        if not (
            effective_api_key := (
                api_key
                or config.api_key
                or LLMClientFactory._get_api_key_from_env(config.provider)
            )
        ):
            raise ValueError(
                f"API key required for {config.provider}. Set it via parameter, config, or environment variable."
            )

        if config.provider == "gemini":
            return GeminiLLMClient(GeminiClient(api_key=effective_api_key))
        elif config.provider == "openai":
            return OpenAILLMClient(OpenAI(api_key=effective_api_key))
        elif config.provider == "claude":
            return AnthropicLLMClient(Anthropic(api_key=effective_api_key))
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    @staticmethod
    def _get_api_key_from_env(provider: str) -> str | None:
        """Get API key from environment variables."""
        env_var = {
            "gemini": "GOOGLE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }.get(provider)

        if env_var and (api_key := os.getenv(env_var)):
            logger.info(f"Using API key from environment variable: {env_var}")
            return api_key

        logger.warning(f"No API key found for {provider}")
        return None
