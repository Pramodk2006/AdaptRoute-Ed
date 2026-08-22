"""
Quiz generation prompt template.

Generates MCQ quizzes for a given topic.
"""


def build_quiz_prompt(
    topic_title: str,
    topic_description: str,
    skill_level: str,
    num_questions: int = 5,
) -> str:
    """
    Build a prompt that generates MCQ questions for a topic.

    Args:
        topic_title: The topic being assessed.
        topic_description: Short description of the topic.
        skill_level: beginner | intermediate | advanced
        num_questions: Number of MCQ questions to generate.

    Returns:
        A prompt string enforcing JSON output with MCQ questions.
    """
    return f"""You are an expert educational assessment designer.

Generate {num_questions} multiple-choice quiz questions to assess a student's understanding of:
- Topic: {topic_title}
- Description: {topic_description}
- Student Level: {skill_level}

Question Guidelines:
1. Questions must test genuine understanding, not just memorisation.
2. Each question must have exactly 4 options labelled A, B, C, D.
3. Only one option is correct.
4. Provide a clear explanation for why the correct answer is right.
5. Difficulty should match the {skill_level} level.
6. Avoid ambiguous or trick questions.

Respond with ONLY the following JSON structure:

{{
  "title": "Quiz: {topic_title}",
  "questions": [
    {{
      "order_index": 0,
      "question_text": "What is ...?",
      "question_type": "mcq",
      "options": [
        {{"label": "A", "text": "Option A text"}},
        {{"label": "B", "text": "Option B text"}},
        {{"label": "C", "text": "Option C text"}},
        {{"label": "D", "text": "Option D text"}}
      ],
      "correct_answer": "A",
      "explanation": "Option A is correct because ..."
    }}
  ]
}}"""
