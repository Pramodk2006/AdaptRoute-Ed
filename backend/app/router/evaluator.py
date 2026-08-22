"""
Response Quality Evaluator — heuristic scoring of LLM outputs.

v1 uses structural heuristics (no additional LLM call, zero latency overhead).
Designed to be swapped for an LLM-as-judge evaluator in a future version.

Score formula is task-dependent:

  quality = Σ  weight_i × dimension_score_i   ∈ [0.0, 1.0]

Dimensions evaluated:
  - completeness:         Did the response actually address the prompt?
  - length_adequacy:      Is response length appropriate for the task?
  - structure:            Does it use expected formatting (JSON, headers, etc.)?
  - instruction_following: Did it produce the right output type?
  - coherence:            Basic language quality proxy (no truncation, etc.)
"""
import json
import re
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class QualityReport:
    overall: float                          # 0.0 – 1.0  (weighted total)
    completeness: float = 0.0
    length_adequacy: float = 0.0
    structure: float = 0.0
    instruction_following: float = 0.0
    coherence: float = 0.0
    notes: list = field(default_factory=list)


# ── Per-task quality weight profiles ─────────────────────────────────────────
_QUALITY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "roadmap": {
        "completeness":          0.30,
        "length_adequacy":       0.25,
        "structure":             0.25,
        "instruction_following": 0.15,
        "coherence":             0.05,
    },
    "quiz": {
        "completeness":          0.25,
        "length_adequacy":       0.15,
        "structure":             0.35,   # JSON compliance critical
        "instruction_following": 0.20,
        "coherence":             0.05,
    },
    "code_example": {
        "completeness":          0.25,
        "length_adequacy":       0.20,
        "structure":             0.25,   # code blocks present
        "instruction_following": 0.25,
        "coherence":             0.05,
    },
    "explanation": {
        "completeness":          0.35,
        "length_adequacy":       0.25,
        "structure":             0.10,
        "instruction_following": 0.20,
        "coherence":             0.10,
    },
    "socratic": {
        "completeness":          0.30,
        "length_adequacy":       0.15,
        "structure":             0.10,
        "instruction_following": 0.30,
        "coherence":             0.15,
    },
    "default": {
        "completeness":          0.30,
        "length_adequacy":       0.20,
        "structure":             0.20,
        "instruction_following": 0.20,
        "coherence":             0.10,
    },
}

# Expected minimum output lengths per task type (chars)
_MIN_LENGTH: Dict[str, int] = {
    "roadmap":      800,
    "quiz":         400,
    "code_example": 300,
    "explanation":  200,
    "socratic":     100,
    "default":      150,
}

# Expected maximum useful output length (penalty zone above this)
_MAX_LENGTH: Dict[str, int] = {
    "roadmap":      8000,
    "quiz":         3000,
    "code_example": 4000,
    "explanation":  2000,
    "socratic":     800,
    "default":      2000,
}


def evaluate_response(
    response_text: str,
    task_type: str,
    prompt: str,
    requires_json: bool = False,
    requires_code: bool = False,
) -> QualityReport:
    """
    Score a model response against task expectations.

    All scores are 0.0–1.0. The overall score is a weighted average using
    per-task dimension weights.

    Args:
        response_text:  Raw text from the LLM (may include JSON or code).
        task_type:      Task category for weight and length profiles.
        prompt:         Original user prompt (used to check relevance).
        requires_json:  True if response must contain valid JSON.
        requires_code:  True if response must contain a code block.
    """
    text = (response_text or "").strip()
    notes = []

    # ── Dimension 1: Completeness ─────────────────────────────────────────────
    # Proxy: does the response appear to have a conclusion / not be cut off?
    completeness = 1.0
    if len(text) < 50:
        completeness = 0.10
        notes.append("Response too short — likely empty or error message.")
    elif text.endswith(("...", "…")):
        completeness = 0.60
        notes.append("Response appears truncated.")
    elif len(text) < _MIN_LENGTH.get(task_type, 150) * 0.5:
        completeness = 0.55
        notes.append("Response shorter than half the expected minimum length.")

    # ── Dimension 2: Length adequacy ─────────────────────────────────────────
    min_len = _MIN_LENGTH.get(task_type, _MIN_LENGTH["default"])
    max_len = _MAX_LENGTH.get(task_type, _MAX_LENGTH["default"])
    n = len(text)

    if n >= min_len and n <= max_len:
        length_adequacy = 1.0
    elif n < min_len:
        # Linear penalty below minimum
        length_adequacy = max(0.0, n / min_len)
        notes.append(f"Response length {n} below expected minimum {min_len}.")
    else:
        # Very long responses get mild penalty (possible hallucination/rambling)
        excess = n - max_len
        length_adequacy = max(0.60, 1.0 - (excess / max_len) * 0.4)

    # ── Dimension 3: Structure ────────────────────────────────────────────────
    structure = 0.5  # baseline

    if requires_json:
        # Extract JSON block if present
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                json.loads(json_match.group())
                structure = 1.0
            except json.JSONDecodeError:
                structure = 0.30
                notes.append("Response contained malformed JSON.")
        else:
            structure = 0.10
            notes.append("Required JSON not found in response.")
    elif requires_code:
        if "```" in text:
            structure = 1.0
        elif any(kw in text for kw in ("def ", "class ", "function ", "int main")):
            structure = 0.75
            notes.append("Code present but not in fenced code block.")
        else:
            structure = 0.20
            notes.append("Required code block not found.")
    else:
        # Non-JSON, non-code tasks: check for organisational markers
        has_headers = bool(re.search(r"^#{1,3} .+", text, re.MULTILINE))
        has_bullets = bool(re.search(r"^[\-\*•] .+", text, re.MULTILINE))
        has_numbering = bool(re.search(r"^\d+[\.\)] .+", text, re.MULTILINE))
        markers = sum([has_headers, has_bullets, has_numbering])
        structure = 0.50 + markers * 0.17  # max 1.01, clamp below

    structure = min(structure, 1.0)

    # ── Dimension 4: Instruction following ───────────────────────────────────
    # Proxy: do key terms from the prompt appear in the response?
    prompt_keywords = set(
        w.lower() for w in re.split(r"\W+", prompt) if len(w) > 4
    )
    response_words = set(
        w.lower() for w in re.split(r"\W+", text) if len(w) > 4
    )
    overlap = len(prompt_keywords & response_words)
    if len(prompt_keywords) > 0:
        instruction_following = min(1.0, overlap / min(len(prompt_keywords), 8))
    else:
        instruction_following = 0.70  # neutral

    # Penalise refusals
    refusal_phrases = (
        "i cannot", "i'm unable", "i can't", "as an ai", "i don't have access"
    )
    if any(p in text.lower() for p in refusal_phrases):
        instruction_following = max(0.0, instruction_following - 0.40)
        notes.append("Response contains refusal or disclaimer language.")

    # ── Dimension 5: Coherence ────────────────────────────────────────────────
    # Proxy: paragraph variety and no repeated sentence starts
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    coherence = 0.70  # baseline

    if len(sentences) >= 3:
        starts = [s[:30].lower() for s in sentences]
        unique_starts = len(set(starts))
        repeat_ratio = 1.0 - (unique_starts / max(len(starts), 1))
        if repeat_ratio > 0.5:
            coherence = 0.40
            notes.append("High sentence-start repetition detected.")
        else:
            coherence = min(1.0, 0.70 + unique_starts / max(len(starts), 1) * 0.30)

    # ── Weighted overall score ────────────────────────────────────────────────
    weights = _QUALITY_WEIGHTS.get(task_type, _QUALITY_WEIGHTS["default"])
    overall = (
        weights["completeness"]          * completeness
        + weights["length_adequacy"]     * length_adequacy
        + weights["structure"]           * structure
        + weights["instruction_following"] * instruction_following
        + weights["coherence"]           * coherence
    )
    overall = round(min(max(overall, 0.0), 1.0), 4)

    return QualityReport(
        overall=overall,
        completeness=round(completeness, 3),
        length_adequacy=round(length_adequacy, 3),
        structure=round(structure, 3),
        instruction_following=round(instruction_following, 3),
        coherence=round(coherence, 3),
        notes=notes,
    )
