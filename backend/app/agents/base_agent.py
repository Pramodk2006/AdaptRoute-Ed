"""
Base Agent Interface — foundation for all specialized AI agents in AdaptRoute-Edu.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from app.llm.base import LLMProvider, LLMResponse
from app.llm.factory import get_provider


class BaseAgent(ABC):
    """Abstract base class for specialized agents."""

    def __init__(self, agent_name: str, task_type: str = "explanation"):
        self.agent_name = agent_name
        self.task_type = task_type

    def get_llm(
        self,
        prompt: str,
        user_skill_level: str = "beginner",
        forced_model: Optional[str] = None,
    ) -> LLMProvider:
        """Get LLM provider routed via the Adaptive Router Engine."""
        return get_provider(
            task_type=self.task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            forced_model=forced_model,
        )

    async def generate_adaptive(
        self,
        db_session,
        prompt: str,
        user_id,
        user_skill_level: str = "beginner",
        forced_model: Optional[str] = None,
        is_json: bool = False,
        **generation_kwargs,
    ) -> LLMResponse:
        """Execute content generation through the centralized adaptive feedback pipeline."""
        from app.services.adaptive_llm_service import AdaptiveLLMService
        return await AdaptiveLLMService.generate(
            db_session=db_session,
            user_id=user_id,
            task_type=self.task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            forced_model=forced_model,
            is_json=is_json,
            **generation_kwargs,
        )

    async def generate_adaptive_stream(
        self,
        db_session,
        prompt: str,
        user_id,
        user_skill_level: str = "beginner",
        forced_model: Optional[str] = None,
        **generation_kwargs,
    ):
        """Execute token streaming through the centralized adaptive feedback pipeline."""
        from app.services.adaptive_llm_service import AdaptiveLLMService
        async for chunk in AdaptiveLLMService.generate_stream(
            db_session=db_session,
            user_id=user_id,
            task_type=self.task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            forced_model=forced_model,
            **generation_kwargs,
        ):
            yield chunk

    @abstractmethod
    async def process(self, context: Dict) -> Dict:
        """Process agent task given input context."""
        pass
