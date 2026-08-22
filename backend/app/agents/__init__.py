"""
Agents package — specialized multi-agent tutoring network.
"""
from app.agents.base_agent import BaseAgent
from app.agents.curriculum_agent import CurriculumPlanningAgent
from app.agents.diagnostic_agent import DiagnosticCriticAgent
from app.agents.socratic_agent import SocraticTutorAgent
from app.agents.orchestrator import multi_agent_orchestrator, MultiAgentOrchestrator

__all__ = [
    "BaseAgent",
    "CurriculumPlanningAgent",
    "DiagnosticCriticAgent",
    "SocraticTutorAgent",
    "MultiAgentOrchestrator",
    "multi_agent_orchestrator",
]
