"""
Diagnostic Critic Agent — analyzes quiz responses to pinpoint underlying student misconceptions.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent


class DiagnosticCriticAgent(BaseAgent):
    """Specialized Agent analyzing wrong quiz answers for cognitive misconceptions."""

    def __init__(self):
        super().__init__(agent_name="DiagnosticCriticAgent", task_type="explanation")

    async def process(self, context: Dict) -> Dict:
        """
        Diagnose student misconceptions from quiz attempt data.

        Context expected:
            topic_title: str
            incorrect_answers: List[Dict] -> [{question_text, given_answer, correct_answer, explanation}]
            skill_level: str
        """
        topic_title = context.get("topic_title", "General Topic")
        incorrect_answers: List[Dict] = context.get("incorrect_answers", [])
        skill_level = context.get("skill_level", "beginner")

        if not incorrect_answers:
            return {
                "agent": self.agent_name,
                "has_misconceptions": False,
                "misconception_analysis": "No incorrect answers observed. Excellent understanding demonstrated!",
            }

        formatted_wrong = "\n".join(
            f"Q: {item.get('question_text', '')}\n"
            f"  Given Answer: {item.get('given_answer', 'None')}\n"
            f"  Correct Answer: {item.get('correct_answer', '')}\n"
            for item in incorrect_answers[:5]
        )

        prompt = f"""You are the Diagnostic Critic Agent for an AI Tutoring platform.

Topic: "{topic_title}"
Student Skill Level: {skill_level}

Incorrect Answers Observed:
{formatted_wrong}

Analyze these errors and identify the root misconception pattern in 2-3 concise bullet points. Focus on WHY the student made these specific mistakes."""

        provider = self.get_llm(prompt, user_skill_level=skill_level)
        response = await provider.generate(prompt=prompt, max_tokens=384)
        text_content = response.text if hasattr(response, "text") else str(response)

        return {
            "agent": self.agent_name,
            "has_misconceptions": True,
            "misconception_analysis": text_content.strip(),
        }
