"""
Multi-Agent Orchestrator — coordinates collaboration between specialized agents.
"""
from typing import Dict, Optional, Any
from app.agents.curriculum_agent import CurriculumPlanningAgent
from app.agents.diagnostic_agent import DiagnosticCriticAgent
from app.agents.socratic_agent import SocraticTutorAgent


class MultiAgentOrchestrator:
    """Central Orchestrator coordinating Curriculum, Diagnostic, and Socratic Agents."""

    def __init__(self):
        self.curriculum_agent = CurriculumPlanningAgent()
        self.diagnostic_agent = DiagnosticCriticAgent()
        self.socratic_agent = SocraticTutorAgent()

    async def run_socratic_dialogue(
        self,
        topic_title: str,
        user_message: str,
        history: list,
        user_id: Any = None,
        db_session: Any = None,
        skill_level: str = "beginner",
        mastery_score: Optional[float] = None,
    ) -> Dict:
        """
        Execute Socratic dialogue pipeline:
        1. Curriculum agent provides tone/depth directive if mastery score available.
        2. Socratic agent generates guided response.
        """
        directive = None
        if mastery_score is not None:
            curriculum_res = await self.curriculum_agent.process({
                "topic_title": topic_title,
                "mastery_score": mastery_score,
                "skill_level": skill_level,
                "db_session": db_session,
                "user_id": user_id,
            })
            directive = curriculum_res.get("directive")

        socratic_res = await self.socratic_agent.process({
            "topic_title": topic_title,
            "user_message": user_message,
            "history": history,
            "skill_level": skill_level,
            "db_session": db_session,
            "user_id": user_id,
        })

        return {
            "reply": socratic_res["reply"],
            "curriculum_directive": directive,
            "orchestrated_by": "MultiAgentOrchestrator",
        }

    async def run_diagnostic_analysis(
        self,
        topic_title: str,
        incorrect_answers: list,
        skill_level: str = "beginner",
    ) -> Dict:
        """Execute Diagnostic Agent to analyze quiz failures."""
        return await self.diagnostic_agent.process({
            "topic_title": topic_title,
            "incorrect_answers": incorrect_answers,
            "skill_level": skill_level,
        })


# Global Multi-Agent Orchestrator instance
multi_agent_orchestrator = MultiAgentOrchestrator()
