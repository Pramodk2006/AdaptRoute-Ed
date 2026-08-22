"""
Roadmap generation prompt template.

The LLM is instructed to return a strictly structured JSON object.
The JSON schema is enforced here so the roadmap_service can parse
reliably without fragile string manipulation.
"""


def build_roadmap_prompt(
    learning_goal: str,
    skill_level: str,
    preferred_pace: str,
    daily_study_time_minutes: int,
    num_weeks: int = 8,
) -> str:
    """
    Build the prompt sent to the LLM for generating a personalised roadmap.

    Args:
        learning_goal: What the student wants to learn.
        skill_level: beginner | intermediate | advanced
        preferred_pace: slow | moderate | fast
        daily_study_time_minutes: How many minutes per day the student can study.
        num_weeks: Total weeks for the roadmap.

    Returns:
        A formatted prompt string.
    """
    pace_map = {"slow": "fewer topics", "moderate": "balanced topics", "fast": "more topics"}
    pace_note = pace_map.get(preferred_pace, "balanced topics")

    return f"""You are an expert educational curriculum designer.

Create a {num_weeks}-week personalised learning roadmap for a student with the following profile:
- Learning Goal: {learning_goal}
- Current Skill Level: {skill_level}
- Preferred Pace: {preferred_pace} ({pace_note} per week)
- Daily Study Time: {daily_study_time_minutes} minutes per day

Rules:
1. Divide the content logically across {num_weeks} weeks.
2. Each week should have 2–5 topics appropriate for the skill level.
3. Order topics from foundational to advanced progressively.
4. Each topic should be completable within 1–2 study sessions.
5. Topic titles must be concise and specific (e.g., "Python Variables and Data Types", not "Python Basics").

Respond with ONLY the following JSON structure. Do not add any text outside it:

{{
  "title": "Learning Roadmap: <brief title>",
  "goal": "<restate the learning goal clearly>",
  "total_weeks": {num_weeks},
  "weeks": [
    {{
      "week_number": 1,
      "theme": "Week theme or focus area",
      "topics": [
        {{
          "title": "Topic title",
          "description": "One sentence describing what this topic covers.",
          "order_index": 0
        }}
      ]
    }}
  ]
}}"""
