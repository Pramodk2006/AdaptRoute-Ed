"""
LLM Factory — returns the appropriate provider dynamically guided by the Adaptive Router Engine.
"""
from typing import Optional
from app.llm.base import LLMProvider
from app.config import get_settings
from app.router import router_engine
from app.utils.logger import logger

settings = get_settings()


def _build_registry() -> dict:
    from app.llm.ollama_provider import OllamaProvider
    from app.llm.huggingface_provider import HuggingFaceProvider

    return {
        "ollama": OllamaProvider,
        "huggingface": HuggingFaceProvider,
    }


def get_provider(
    task_type: str = "default",
    prompt: str = "",
    user_skill_level: str = "beginner",
    preferred_pace: str = "moderate",
    daily_study_time: int = 60,
    forced_model: Optional[str] = None,
) -> LLMProvider:
    """
    Return an LLMProvider instance dynamically selected by the Adaptive Router Engine.

    Args:
        task_type:         The generation task category (roadmap, quiz, code_example, etc.).
        prompt:            Task prompt used for capability-requirement feature extraction.
        user_skill_level:  Student skill context (beginner | intermediate | advanced).
        preferred_pace:    Student preferred learning pace (slow | moderate | fast).
        daily_study_time:  Student daily study time in minutes.
        forced_model:      Optional manual model override.
    """
    registry = _build_registry()
    provider_name = settings.LLM_PROVIDER.lower()

    if provider_name not in registry:
        logger.warning(
            f"Provider '{provider_name}' not recognized. Falling back to Ollama."
        )
        provider_name = "ollama"

    # Three-stage adaptive routing
    route_decision = router_engine.route_task(
        task_type=task_type,
        prompt=prompt,
        user_skill_level=user_skill_level,
        preferred_pace=preferred_pace,
        daily_study_time=daily_study_time,
        forced_model=forced_model,
    )
    selected_model = route_decision["selected_model"]
    candidates = route_decision.get("candidates", [])

    logger.info(
        f"🤖 Router → '{selected_model}' for task='{task_type}' "
        f"[policy={route_decision['routing_policy_used']}, "
        f"candidates={len(candidates)}]"
    )

    provider_class = registry[provider_name]
    return provider_class(model=selected_model)
