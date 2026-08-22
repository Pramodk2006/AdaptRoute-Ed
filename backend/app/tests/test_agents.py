"""
Multi-Agent tutoring system unit tests (with mocked LLM providers).
"""
from unittest.mock import AsyncMock, patch
import pytest

from app.agents.curriculum_agent import CurriculumPlanningAgent
from app.agents.diagnostic_agent import DiagnosticCriticAgent
from app.agents.socratic_agent import SocraticTutorAgent
from app.agents.orchestrator import MultiAgentOrchestrator


@pytest.fixture
def mock_llm_generate():
    """Mock LLMProvider.generate to return deterministic agent responses."""
    with patch("app.agents.base_agent.BaseAgent.get_llm") as mock_get_llm:
        mock_provider = AsyncMock()
        mock_provider.generate = AsyncMock(return_value="Agent response generated for testing.")
        mock_get_llm.return_value = mock_provider
        yield mock_provider


@pytest.mark.asyncio
async def test_curriculum_planning_agent(mock_llm_generate):
    """Curriculum agent provides remediation directive for low mastery."""
    agent = CurriculumPlanningAgent()
    res = await agent.process({
        "topic_title": "Binary Search Trees",
        "mastery_score": 0.30,
        "skill_level": "beginner",
    })
    assert res["agent"] == "CurriculumPlanningAgent"
    assert res["recommend_remediation"] is True
    assert res["recommend_advanced"] is False
    assert len(res["directive"]) > 0


@pytest.mark.asyncio
async def test_curriculum_planning_agent_advanced(mock_llm_generate):
    """Curriculum agent recommends advanced exercises for high mastery."""
    agent = CurriculumPlanningAgent()
    res = await agent.process({
        "topic_title": "Binary Search Trees",
        "mastery_score": 0.90,
        "skill_level": "advanced",
    })
    assert res["recommend_remediation"] is False
    assert res["recommend_advanced"] is True


@pytest.mark.asyncio
async def test_diagnostic_critic_agent_no_errors(mock_llm_generate):
    """Diagnostic agent handles clean quiz attempts without misconceptions."""
    agent = DiagnosticCriticAgent()
    res = await agent.process({
        "topic_title": "Recursion",
        "incorrect_answers": [],
    })
    assert res["has_misconceptions"] is False


@pytest.mark.asyncio
async def test_diagnostic_critic_agent_with_errors(mock_llm_generate):
    """Diagnostic agent analyzes wrong answers."""
    agent = DiagnosticCriticAgent()
    res = await agent.process({
        "topic_title": "Recursion",
        "incorrect_answers": [
            {
                "question_text": "What is the base case in recursion?",
                "given_answer": "A function calling itself",
                "correct_answer": "The condition that stops recursion",
            }
        ],
    })
    assert res["has_misconceptions"] is True
    assert len(res["misconception_analysis"]) > 0


@pytest.mark.asyncio
async def test_socratic_tutor_agent(mock_llm_generate):
    """Socratic agent generates guided response."""
    agent = SocraticTutorAgent()
    res = await agent.process({
        "topic_title": "Python Decorators",
        "user_message": "What is a wrapper function?",
        "history": [],
        "skill_level": "intermediate",
    })
    assert res["agent"] == "SocraticTutorAgent"
    assert len(res["reply"]) > 0


@pytest.mark.asyncio
async def test_multi_agent_orchestrator(mock_llm_generate):
    """Orchestrator coordinates Socratic & Curriculum agents."""
    orchestrator = MultiAgentOrchestrator()
    res = await orchestrator.run_socratic_dialogue(
        topic_title="Graph Traversal BFS",
        user_message="Why do we use a queue for BFS?",
        history=[],
        mastery_score=0.40,
    )
    assert "reply" in res
    assert "curriculum_directive" in res
    assert res["orchestrated_by"] == "MultiAgentOrchestrator"


def test_socratic_api_endpoint(client, auth_headers, mock_llm_generate):
    """POST /api/v1/socratic/chat returns orchestrated Socratic response."""
    payload = {
        "topic_title": "Linked Lists",
        "user_message": "How do I reverse a singly linked list?",
        "history": [],
        "skill_level": "beginner",
    }
    response = client.post("/api/v1/socratic/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "orchestrated_by" in data
