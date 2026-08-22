"""
Content generation prompt template.

Generates study notes, explanation, and examples for a given topic.
"""


def build_content_prompt(
    topic_title: str,
    topic_description: str,
    skill_level: str,
    learning_goal: str,
) -> str:
    """
    Build a prompt that produces structured study content for one topic.

    Returns:
        A prompt string enforcing JSON output with notes, explanation, examples.
    """
    return f"""You are an expert tutor generating educational content for a student.

Student Profile:
- Learning Goal: {learning_goal}
- Skill Level: {skill_level}

Generate comprehensive study material for the following topic:
- Topic: {topic_title}
- Description: {topic_description}

Guidelines:
1. Adjust complexity to the student's skill level ({skill_level}).
2. Notes should be clear, concise bullet points covering key concepts.
3. Explanation should be a detailed paragraph in plain language.
4. Examples should be concrete, practical, and runnable (code examples where relevant).
5. Use simple language for beginners, technical depth for advanced learners.

Respond with ONLY the following JSON structure:

{{
  "notes": [
    "Key concept or point 1",
    "Key concept or point 2",
    "Key concept or point 3"
  ],
  "explanation": "A clear, detailed paragraph explaining the topic in depth for a {skill_level} learner.",
  "examples": [
    {{
      "title": "Example title",
      "content": "Code or explanation of the example",
      "language": "python"
    }}
  ]
}}"""
