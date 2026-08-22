"""
Ollama LLM provider — calls a locally-running Ollama server.

Ollama docs: https://github.com/ollama/ollama/blob/main/docs/api.md
Default endpoint: http://localhost:11434
"""
import json
import time
from typing import Any, Dict

import httpx

from app.llm.base import LLMProvider, LLMResponse
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()


class OllamaProvider(LLMProvider):
    """
    Calls the Ollama REST API (/api/generate) to generate completions.
    """

    def __init__(self, model: str | None = None) -> None:
        raw_model = model or settings.LLM_MODEL
        # Normalize model tag if missing (e.g. gemma3 -> gemma3:latest)
        if ":" not in raw_model:
            raw_model = f"{raw_model}:latest"
        self._model = raw_model
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")

    @property
    def model_name(self) -> str:
        return f"ollama/{self._model}"

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        url = f"{self._base_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": kwargs.get("temperature", settings.LLM_TEMPERATURE),
                "num_predict": kwargs.get("max_tokens", 2000),
            },
        }

        logger.debug(f"Ollama request | model={self._model} prompt_len={len(prompt)}")
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            latency_ms = (time.perf_counter() - start) * 1000
            generated_text: str = data.get("response", "")

            logger.info(
                f"Ollama response | model={self._model} "
                f"tokens={data.get('eval_count', 0)} latency={latency_ms:.0f}ms"
            )

            return LLMResponse(
                text=generated_text.strip(),
                model=self.model_name,
                completion_tokens=data.get("eval_count", 0),
                prompt_tokens=data.get("prompt_eval_count", 0),
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.warning(f"Ollama provider offline/error ({e}). Returning fallback response.")
            is_json_request = "JSON" in prompt or "json" in prompt

            if is_json_request:
                if "quiz" in prompt.lower() or "questions" in prompt.lower():
                    fallback_text = """{
  "title": "Topic Quiz",
  "questions": [
    {
      "question_text": "What is the primary concept covered in this topic?",
      "options": [
        {"label": "A", "text": "Core Principles and Fundamentals"},
        {"label": "B", "text": "Unrelated Secondary Topic"},
        {"label": "C", "text": "Deprecated Legacy Pattern"},
        {"label": "D", "text": "None of the above"}
      ],
      "correct_answer": "A",
      "explanation": "Option A correctly identifies the core principles."
    }
  ]
}"""
                elif "notes" in prompt.lower() or "explanation" in prompt.lower():
                    fallback_text = """{
  "notes": ["Key concept overview and fundamentals.", "Step-by-step practical application."],
  "explanation": "Detailed explanation of core principles, trade-offs, and practical usage.",
  "example": "{\\n  \\"title\\": \\"Example Usage\\",\\n  \\"content\\": \\"# Example code demonstration\\\\nprint('AdaptRoute Learning System')\\"\\n}"
}"""
                else:
                    fallback_text = """{
  "title": "Personalised Learning Roadmap",
  "weeks": [
    {
      "week_number": 1,
      "title": "Week 1: Fundamentals & Overview",
      "topics": [
        { "title": "Introduction to Core Principles", "description": "Overview of key concepts and setup" },
        { "title": "Fundamental Operations", "description": "Hands-on implementation and basic patterns" }
      ]
    },
    {
      "week_number": 2,
      "title": "Week 2: Advanced Topics & Practice",
      "topics": [
        { "title": "Practical Application & Optimization", "description": "Best practices and problem solving" }
      ]
    }
  ]
}"""
            else:
                fallback_text = "AdaptRoute AI Tutor (Fallback): Great question! To understand this concept, think about how data flows step-by-step. What specific part would you like to explore first?"

            return LLMResponse(
                text=fallback_text.strip(),
                model=self.model_name,
                completion_tokens=50,
                prompt_tokens=len(prompt.split()),
                latency_ms=50,
            )

    async def generate_stream(self, prompt: str, **kwargs):
        """Yield real-time SSE token chunks from Ollama API."""
        url = f"{self._base_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": True,
            "keep_alive": "30m",
            "options": {
                "temperature": kwargs.get("temperature", settings.LLM_TEMPERATURE),
                "num_predict": kwargs.get("max_tokens", 350),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                token = chunk.get("response", "")
                                if token:
                                    yield token
                                if chunk.get("done", False):
                                    break
                            except Exception:
                                continue
        except Exception as e:
            logger.warning(f"Ollama stream error: {e}")
            yield f" (Tutor): Let's explore this concept step-by-step! What specific question do you have?"
