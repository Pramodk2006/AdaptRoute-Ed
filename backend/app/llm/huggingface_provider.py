"""
HuggingFace Transformers LLM provider.

Uses the transformers pipeline API with a locally loaded model.
Heavier setup but gives full control over the model weights.

Requirements (install separately):
    pip install transformers torch accelerate
"""
import time
from typing import Any

from app.llm.base import LLMProvider, LLMResponse
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()


class HuggingFaceProvider(LLMProvider):
    """
    Loads a HuggingFace model locally via the transformers pipeline.

    The model is loaded lazily on first call to avoid slowing startup
    when Ollama is the active provider.
    """

    def __init__(self, model_id: str | None = None) -> None:
        self._model_id = model_id or settings.HUGGINGFACE_MODEL_ID
        self._pipeline = None  # Lazy-loaded

    @property
    def model_name(self) -> str:
        return f"huggingface/{self._model_id}"

    def _load_pipeline(self) -> Any:
        """Load the HuggingFace text-generation pipeline (lazy)."""
        try:
            from transformers import pipeline
            import torch

            logger.info(f"Loading HuggingFace model: {self._model_id}")
            pipe = pipeline(
                "text-generation",
                model=self._model_id,
                token=settings.HUGGINGFACE_TOKEN or None,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            logger.info(f"HuggingFace model loaded: {self._model_id}")
            return pipe
        except ImportError:
            raise RuntimeError(
                "transformers and torch are required for HuggingFaceProvider. "
                "Run: pip install transformers torch accelerate"
            )

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if self._pipeline is None:
            self._pipeline = self._load_pipeline()

        max_tokens = kwargs.get("max_tokens", settings.LLM_MAX_TOKENS)
        temperature = kwargs.get("temperature", settings.LLM_TEMPERATURE)

        logger.debug(f"HuggingFace request | model={self._model_id}")
        start = time.perf_counter()

        # HuggingFace pipeline is synchronous — wrap in executor for async contexts
        import asyncio

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._pipeline(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                return_full_text=False,
            ),
        )

        latency_ms = (time.perf_counter() - start) * 1000
        generated_text: str = result[0]["generated_text"] if result else ""

        logger.info(f"HuggingFace response | latency={latency_ms:.0f}ms")

        return LLMResponse(
            text=generated_text.strip(),
            model=self.model_name,
            latency_ms=latency_ms,
        )
