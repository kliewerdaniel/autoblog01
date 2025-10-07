"""
LLM Client for interacting with Ollama models.

Provides a clean interface for chat completions, streaming, and token counting.
"""

import sys
import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import httpx

# Handle both module and direct execution contexts
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from .config import config
    from .models import LLMMesssage, LLMResponse
except ImportError:
    from config import config
    from models import LLMMesssage, LLMResponse

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""
    pass


class ModelNotFoundError(OllamaError):
    """Raised when the specified model is not available."""
    pass


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, model: str = None, base_url: str = None, timeout: int = None):
        self.model = model or config.ollama_model
        self.base_url = base_url or config.ollama_base_url
        self.timeout = timeout or config.ollama_timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def is_model_available(self) -> bool:
        """Check if the model is available in Ollama."""
        try:
            # This would need to be async, but we'll make it sync for simplicity
            # In practice, this should be called with await
            import subprocess
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self.model in result.stdout
        except Exception as e:
            logger.warning(f"Could not check model availability: {e}")
            return False

    async def chat(
        self,
        messages: List[Union[LLMMesssage, Dict[str, str]]],
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> str:
        """
        Send a chat completion request to Ollama.

        Args:
            messages: List of messages with role/content
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text content
        """
        if temperature is None:
            temperature = config.temperature
        if max_tokens is None:
            max_tokens = config.max_tokens

        # Convert messages to expected format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, LLMMesssage):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                formatted_messages.append(msg)

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        for attempt in range(config.max_retries):
            try:
                response = await self.client.post("/api/chat", json=payload)

                if response.status_code != 200:
                    if response.status_code == 404:
                        raise ModelNotFoundError(f"Model '{self.model}' not found")
                    raise OllamaError(f"HTTP {response.status_code}: {response.text}")

                if stream:
                    return await self._handle_stream_response(response)
                else:
                    data = response.json()
                    return data.get("message", {}).get("content", "")

            except httpx.TimeoutException:
                if attempt < config.max_retries - 1:
                    delay = config.retry_delay * (config.retry_backoff ** attempt)
                    logger.warning(f"Request timed out, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise OllamaError("Request timed out after all retries")
            except httpx.RequestError as e:
                if attempt < config.max_retries - 1:
                    delay = config.retry_delay * (config.retry_backoff ** attempt)
                    logger.warning(f"Request error: {e}, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise OllamaError(f"Request failed after retries: {e}")

    async def _handle_stream_response(self, response: httpx.Response) -> str:
        """Handle streaming response from Ollama."""
        content = ""
        async for line in response.aiter_lines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        chunk = data["message"]["content"]
                        content += chunk
                        # Could emit progress here
                except json.JSONDecodeError:
                    continue
        return content

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None
    ) -> str:
        """
        Generate text using a simple prompt (completion-style).

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return await self.chat(messages, temperature=temperature)

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        This is a rough approximation - in production, use tiktoken or similar.
        """
        # Rough approximation: 1 token ≈ 4 characters for English
        return len(text) // 4

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise OllamaError(f"Failed to get model info: {e}")


# Global LLM client instance
llm_client = OllamaClient()
