"""
Socratic Tutor Agent — guides students through interactive step-by-step Socratic dialogue.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent
from app.rag import global_rag_engine


from app.agents.socratic_dialogue_engine import generate_socratic_response


class SocraticTutorAgent(BaseAgent):
    """Specialized Agent executing interactive Socratic Q&A tutoring sessions."""

    def __init__(self):
        super().__init__(agent_name="SocraticTutorAgent", task_type="explanation")

    async def process(self, context: Dict) -> Dict:
        """
        Generate next Socratic response or guiding question given conversation history.

        Context expected:
            topic_title: str
            user_message: str
            history: List[Dict] -> [{role: "user" | "assistant", content: str}]
            skill_level: str
        """
        topic_title = context.get("topic_title", "General Topic")
        user_message = context.get("user_message", "")
        history: List[Dict] = context.get("history", [])
        skill_level = context.get("skill_level", "beginner")

        formatted_history = ""
        for msg in history[-6:]:  # Keep last 6 exchanges
            role = "Student" if msg.get("role") == "user" else "Socratic Tutor"
            formatted_history += f"{role}: {msg.get('content', '')}\n"

        rag_context, citations = global_rag_engine.retrieve_grounding_context(user_message, top_k=2)
        rag_prompt_section = f"\nGrounded Reference Material:\n{rag_context}\n" if rag_context else ""

        prompt = f"""You are the Socratic Tutor Agent for AdaptRoute-Edu. Your goal is to guide the student to discover the answer themselves through thoughtful, probing questions rather than giving away direct answers.

Topic: "{topic_title}"
Student Skill Level: {skill_level}{rag_prompt_section}
Conversation History:
{formatted_history}

Student's Latest Input: "{user_message}"

Respond as a helpful, encouraging Socratic Tutor:
1. Validate what the student got right (if anything).
2. Ask 1 clear, probing follow-up question that guides them toward the correct concept.
3. Keep your response brief (2-4 sentences max). Do NOT provide a full direct solution directly."""

        db_session = context.get("db_session")
        user_id = context.get("user_id")

        try:
            response = await self.generate_adaptive(
                db_session=db_session,
                prompt=prompt,
                user_id=user_id,
                user_skill_level=skill_level,
                max_tokens=300,
            )
            text_content = response.text if hasattr(response, "text") else str(response)
        except Exception:
            text_content = ""

        # If text content is empty or generic static fallback, generate targeted Socratic dialogue response
        if not text_content or "AdaptRoute AI Tutor (Fallback)" in text_content:
            text_content = generate_socratic_response(topic_title, user_message, history, skill_level)

        return {
            "agent": self.agent_name,
            "reply": text_content.strip(),
        }

    async def process_stream(self, context: Dict):
        """Yield real-time SSE token stream for interactive Socratic Q&A."""
        topic_title = context.get("topic_title", "General Topic")
        user_message = context.get("user_message", "")
        history: List[Dict] = context.get("history", [])
        skill_level = context.get("skill_level", "beginner")
        db_session = context.get("db_session")
        user_id = context.get("user_id")

        formatted_history = ""
        for msg in history[-6:]:
            role = "Student" if msg.get("role") == "user" else "Socratic Tutor"
            formatted_history += f"{role}: {msg.get('content', '')}\n"

        rag_context, _ = global_rag_engine.retrieve_grounding_context(user_message, top_k=2)
        rag_prompt_section = f"\nGrounded Reference Material:\n{rag_context}\n" if rag_context else ""

        prompt = f"""You are the Socratic Tutor Agent for AdaptRoute-Edu. Your goal is to guide the student to discover the answer themselves through thoughtful, probing questions rather than giving away direct answers.

Topic: "{topic_title}"
Student Skill Level: {skill_level}{rag_prompt_section}
Conversation History:
{formatted_history}

Student's Latest Input: "{user_message}"

Respond as a helpful, encouraging Socratic Tutor:
1. Validate what the student got right (if anything).
2. Ask 1 clear, probing follow-up question that guides them toward the correct concept.
3. Keep your response brief (2-4 sentences max). Do NOT provide a full direct solution directly."""

        async for token in self.generate_adaptive_stream(
            db_session=db_session,
            prompt=prompt,
            user_id=user_id,
            user_skill_level=skill_level,
            max_tokens=350,
        ):
            yield token
