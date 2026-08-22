"""
Curriculum Planning Agent — analyzes student mastery state, pace, and goal to formulate optimal learning paths.
"""
from typing import Dict
from app.agents.base_agent import BaseAgent


class CurriculumPlanningAgent(BaseAgent):
    """Specialized Agent responsible for curriculum adjustment & topic depth planning."""

    def __init__(self):
        super().__init__(agent_name="CurriculumPlanningAgent", task_type="roadmap")

    async def process(self, context: Dict) -> Dict:
        """
        Analyze student BKT mastery stats and suggest next learning focus.

        Context expected:
            topic_title: str
            mastery_score: float
            skill_level: str
            preferred_pace: str
        """
        topic_title = context.get("topic_title", "General Topic")
        mastery_score = context.get("mastery_score", 0.25)
        skill_level = context.get("skill_level", "beginner")
        pace = context.get("preferred_pace", "moderate")

        prompt = f"""You are the Curriculum Planning Agent for AdaptRoute-Edu.

Student Profile:
- Current Topic: "{topic_title}"
- Concept Mastery P(L_t): {mastery_score:.2f} (0.0=none, 1.0=mastered)
- Overall Skill Level: {skill_level}
- Learning Pace: {pace}

Provide a short 2-sentence pedagogical directive for the student's next step.
If mastery < 0.50, recommend foundational remediation.
If mastery >= 0.80, recommend advanced challenge problems.
Otherwise, recommend standard practice exercises."""

        provider = self.get_llm(prompt, user_skill_level=skill_level)
        response = await provider.generate(prompt=prompt, max_tokens=256)
        text_content = response.text if hasattr(response, "text") else str(response)

        return {
            "agent": self.agent_name,
            "mastery_score": mastery_score,
            "directive": text_content.strip(),
            "recommend_remediation": mastery_score < 0.50,
            "recommend_advanced": mastery_score >= 0.80,
        }
