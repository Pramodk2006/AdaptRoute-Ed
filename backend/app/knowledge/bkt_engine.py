"""
Bayesian Knowledge Tracing (BKT) Engine.

Standard BKT uses four parameters to model student knowledge over time:
  P(L_0) : Prior probability student knows the skill before any observation
  P(T)   : Probability of learning (transitioning from unknown → known)
  P(S)   : Probability of slip (knows skill but answers incorrectly)
  P(G)   : Probability of guess (doesn't know skill but answers correctly)

Update rules (Corbett & Anderson, 1994):
  After correct response:
    P(L_t | correct) = P(L_{t-1}) * (1 - P(S))
                       ─────────────────────────────────────────────────────
                       P(L_{t-1}) * (1 - P(S)) + (1 - P(L_{t-1})) * P(G)

  After incorrect response:
    P(L_t | incorrect) = P(L_{t-1}) * P(S)
                         ────────────────────────────────────────────────────
                         P(L_{t-1}) * P(S) + (1 - P(L_{t-1})) * (1 - P(G))

  Then apply learning transit:
    P(L_t) = P(L_t|obs) + (1 - P(L_t|obs)) * P(T)
"""
from dataclasses import dataclass


@dataclass
class BKTParams:
    """BKT model hyperparameters per skill domain."""
    p_init: float = 0.25     # P(L_0): prior mastery probability
    p_transit: float = 0.15  # P(T): learning rate
    p_slip: float = 0.10     # P(S): probability of slipping on known concept
    p_guess: float = 0.20    # P(G): probability of guessing on unknown concept


# Default parameters suitable for undergraduate CS/STEM topics
DEFAULT_PARAMS = BKTParams()


def update_mastery(
    current_mastery: float,
    is_correct: bool,
    params: BKTParams = DEFAULT_PARAMS,
) -> float:
    """
    Compute updated P(L_t) after one observed response.

    Args:
        current_mastery: Current P(L_{t-1}) estimate in [0, 1].
        is_correct: Whether the student answered correctly.
        params: BKT hyperparameters.

    Returns:
        Updated mastery probability P(L_t) in [0, 1].
    """
    p_l = current_mastery

    if is_correct:
        numerator = p_l * (1.0 - params.p_slip)
        denominator = numerator + (1.0 - p_l) * params.p_guess
    else:
        numerator = p_l * params.p_slip
        denominator = numerator + (1.0 - p_l) * (1.0 - params.p_guess)

    # Posterior P(L_t | observation)
    p_l_given_obs = numerator / denominator if denominator > 0 else p_l

    # Apply transit (learning) probability
    p_l_new = p_l_given_obs + (1.0 - p_l_given_obs) * params.p_transit

    return round(min(max(p_l_new, 0.0), 1.0), 4)


def batch_update_mastery(
    current_mastery: float,
    correct_count: int,
    total_count: int,
    params: BKTParams = DEFAULT_PARAMS,
) -> float:
    """
    Apply BKT updates for a full quiz attempt (sequence of responses).

    Simulates sequential BKT updates for all items in the attempt.

    Args:
        current_mastery: Starting P(L_0) estimate.
        correct_count: Number of correct answers.
        total_count: Total number of questions.
        params: BKT hyperparameters.

    Returns:
        Final updated mastery probability P(L_t).
    """
    mastery = current_mastery
    incorrect_count = total_count - correct_count

    # Apply correct responses first, then incorrect (approximation)
    for _ in range(correct_count):
        mastery = update_mastery(mastery, is_correct=True, params=params)
    for _ in range(incorrect_count):
        mastery = update_mastery(mastery, is_correct=False, params=params)

    return mastery


MASTERY_THRESHOLD = 0.70   # Student is considered "proficient" at or above this


def needs_remediation(mastery_score: float, quiz_score_pct: float) -> bool:
    """
    Determine whether a student needs adaptive remediation.

    Triggers remediation if:
      - Topic mastery P(L_t) < 0.70, OR
      - Quiz score is below 60%
    """
    return mastery_score < MASTERY_THRESHOLD or quiz_score_pct < 60.0
