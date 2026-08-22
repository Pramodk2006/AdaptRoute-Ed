"""
Task Feature Extractor — converts task metadata & student state into a
12-dimensional capability-requirement vector that represents WHAT the task needs,
not just how complex it is.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskFeatures:
    # ── Metadata ─────────────────────────────────────────────────────────────
    task_type: str                          # roadmap | quiz | code_example | explanation | socratic
    prompt_length_chars: int
    user_skill_level: str                   # beginner | intermediate | advanced
    preferred_pace: str                     # slow | moderate | fast
    daily_study_time: int

    # ── Capability Requirement Scores (0.0 – 1.0) ────────────────────────────
    complexity: float = 0.5
    reasoning_requirement: float = 0.5
    coding_requirement: float = 0.0
    knowledge_requirement: float = 0.5
    output_length_requirement: float = 0.3
    context_requirement: float = 0.3
    structured_output_requirement: float = 0.3
    accuracy_requirement: float = 0.5
    creativity_requirement: float = 0.3

    def to_vector(self) -> List[float]:
        """
        9-element numeric capability-requirement vector for the LinUCB bandit.

        Why 9, not 14?  TaskFeatures has 14 fields total: 5 are non-numeric
        metadata (task_type, prompt_length, user_skill_level, preferred_pace,
        daily_study_time).  Those 5 are consumed by CapabilityFilter via the
        task-profile lookup — the bandit only needs the 9 scalar capability
        scores to learn which model works best in a given capability context.
        """
        return [
            self.complexity,
            self.reasoning_requirement,
            self.coding_requirement,
            self.knowledge_requirement,
            self.output_length_requirement,
            self.context_requirement,
            self.structured_output_requirement,
            self.accuracy_requirement,
            self.creativity_requirement,
        ]


# ── Per-task capability profiles ─────────────────────────────────────────────
_TASK_PROFILES = {
    "roadmap": {
        "complexity": 0.80,
        "reasoning": 0.75,
        "coding": 0.00,
        "knowledge": 0.90,
        "output_length": 0.95,
        "context": 0.90,
        "structured_output": 0.95,
        "accuracy": 0.95,
        "creativity": 0.50,
    },
    "quiz": {
        "complexity": 0.60,
        "reasoning": 0.65,
        "coding": 0.10,
        "knowledge": 0.85,
        "output_length": 0.50,
        "context": 0.60,
        "structured_output": 0.95,
        "accuracy": 0.90,
        "creativity": 0.30,
    },
    "code_example": {
        "complexity": 0.75,
        "reasoning": 0.70,
        "coding": 0.95,
        "knowledge": 0.75,
        "output_length": 0.70,
        "context": 0.70,
        "structured_output": 0.50,
        "accuracy": 0.90,
        "creativity": 0.30,
    },
    "explanation": {
        "complexity": 0.45,
        "reasoning": 0.55,
        "coding": 0.00,
        "knowledge": 0.80,
        "output_length": 0.40,
        "context": 0.45,
        "structured_output": 0.20,
        "accuracy": 0.70,
        "creativity": 0.40,
    },
    "socratic": {
        "complexity": 0.50,
        "reasoning": 0.70,
        "coding": 0.10,
        "knowledge": 0.75,
        "output_length": 0.25,
        "context": 0.65,
        "structured_output": 0.10,
        "accuracy": 0.75,
        "creativity": 0.60,
    },
}

_DEFAULT_PROFILE = {
    "complexity": 0.50,
    "reasoning": 0.50,
    "coding": 0.00,
    "knowledge": 0.50,
    "output_length": 0.30,
    "context": 0.30,
    "structured_output": 0.30,
    "accuracy": 0.50,
    "creativity": 0.30,
}


def extract_features(
    task_type: str,
    prompt: str,
    user_skill_level: str = "beginner",
    preferred_pace: str = "moderate",
    daily_study_time: int = 60,
) -> TaskFeatures:
    """
    Derive a capability-requirement feature vector from task metadata.

    Advanced learners and longer prompts raise several requirement scores
    because they signal richer, longer, more accurate output is expected.
    """
    profile = dict(_TASK_PROFILES.get(task_type, _DEFAULT_PROFILE))
    length = len(prompt)

    # Advanced skill level → higher reasoning & knowledge bar
    if user_skill_level == "advanced":
        profile["reasoning"] = min(1.0, profile["reasoning"] + 0.15)
        profile["knowledge"] = min(1.0, profile["knowledge"] + 0.15)
    elif user_skill_level == "intermediate":
        profile["reasoning"] = min(1.0, profile["reasoning"] + 0.07)
        profile["knowledge"] = min(1.0, profile["knowledge"] + 0.07)

    # Long prompts suggest the student wants richer, longer output
    if length > 1000:
        profile["output_length"] = min(1.0, profile["output_length"] + 0.10)
        profile["context"] = min(1.0, profile["context"] + 0.10)
    elif length > 400:
        profile["output_length"] = min(1.0, profile["output_length"] + 0.05)
        profile["context"] = min(1.0, profile["context"] + 0.05)

    # Code keywords in prompt boost coding requirement
    code_keywords = ("code", "implement", "function", "class", "debug", "algorithm")
    if any(kw in prompt.lower() for kw in code_keywords):
        profile["coding"] = min(1.0, profile["coding"] + 0.20)

    return TaskFeatures(
        task_type=task_type,
        prompt_length_chars=length,
        user_skill_level=user_skill_level,
        preferred_pace=preferred_pace,
        daily_study_time=daily_study_time,
        complexity=profile["complexity"],
        reasoning_requirement=profile["reasoning"],
        coding_requirement=profile["coding"],
        knowledge_requirement=profile["knowledge"],
        output_length_requirement=profile["output_length"],
        context_requirement=profile["context"],
        structured_output_requirement=profile["structured_output"],
        accuracy_requirement=profile["accuracy"],
        creativity_requirement=profile["creativity"],
    )
