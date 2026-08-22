"""
Abstract base class for all LLM providers.

EXTENSION POINT:
    To add a new LLM provider, subclass LLMProvider and implement `generate()`.
    Register it in factory.py. The router will select providers via factory.py.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Structured response from any LLM provider."""
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0


class LLMProvider(ABC):
    """
    Abstract interface that every LLM backend must implement.

    All services interact with this interface only — never with
    a concrete provider directly. This makes swapping or routing
    between providers transparent to the rest of the codebase.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable identifier of the model/provider."""
        ...

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: The full prompt string (system + user content).
            **kwargs: Optional overrides (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated text and metadata.
        """
        ...

    async def generate_json(self, prompt: str, **kwargs) -> str:
        """
        Convenience method that appends JSON enforcement to the prompt
        and returns only the text portion of the response.
        """
        json_prompt = (
            prompt
            + "\n\nIMPORTANT: Respond ONLY with valid JSON. "
            "Do not include any markdown, explanation, or prose outside the JSON."
        )
        response = await self.generate(json_prompt, **kwargs)
        return response.text
