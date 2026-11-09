"""
src/llm/base.py
Abstract base class for LLM providers.
All providers (demo, IBM Granite, future providers) implement this interface.
The rest of the application only calls this interface—never provider-specific code directly.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract LLM provider interface.
    Subclasses implement generate() to call the actual model.
    """

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Generate a response for the given prompt.

        Args:
            prompt: The full prompt string to send to the model.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text response as a string.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of the provider (e.g. 'Demo', 'IBM Granite')."""
        ...

    @property
    def is_demo(self) -> bool:
        """Returns True if this is the demo/mock provider."""
        return False

    def health_check(self) -> dict:
        """
        Optional health check to verify the provider is configured correctly.
        Returns a dict with 'ok' (bool) and 'message' (str).
        """
        return {"ok": True, "message": f"{self.provider_name} is configured."}
