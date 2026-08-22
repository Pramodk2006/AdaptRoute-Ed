"""
AdaptRoute Router Benchmark Suite

Runs a fixed set of representative educational tasks through the router and
records routing decisions, simulated quality scores, and timing.

Usage (from backend/):
    python -m app.router.benchmark

Output: benchmark_results.json  (in backend/)

This is the experiment described in the architecture review:
  - Run 30+ representative tasks across Easy / Medium / Hard categories
  - Record: task, required_capabilities, selected_model, candidates_filtered,
            quality_score, length, routing_policy
  - Verify the router is choosing DIFFERENT models for DIFFERENT tasks,
    not accidentally funnelling everything through one model

Once you have real model responses, replace SIMULATED_RESPONSES with actual
Ollama generations to get real quality scores.
"""
import json
import time
from dataclasses import asdict, dataclass
from typing import Dict, List

from app.router.engine import router_engine
from app.router.evaluator import evaluate_response
from app.router.feature_extractor import extract_features


# ── Benchmark Task Definitions ────────────────────────────────────────────────
BENCHMARK_TASKS = [
    # ── EASY ─────────────────────────────────────────────────────────────────
    {
        "category": "easy",
        "task_type": "explanation",
        "prompt": "What is a variable in programming?",
        "skill_level": "beginner",
        "expected_model_tier": "lightweight",
    },
    {
        "category": "easy",
        "task_type": "explanation",
        "prompt": "Define recursion in simple terms.",
        "skill_level": "beginner",
        "expected_model_tier": "lightweight",
    },
    {
        "category": "easy",
        "task_type": "explanation",
        "prompt": "What is a loop and why do we use it?",
        "skill_level": "beginner",
        "expected_model_tier": "lightweight",
    },
    {
        "category": "easy",
        "task_type": "quiz",
        "prompt": "Generate a 3-question multiple choice quiz on Python variables.",
        "skill_level": "beginner",
        "expected_model_tier": "standard",
    },
    # ── MEDIUM ────────────────────────────────────────────────────────────────
    {
        "category": "medium",
        "task_type": "explanation",
        "prompt": "Explain the difference between stack and heap memory with examples.",
        "skill_level": "intermediate",
        "expected_model_tier": "standard",
    },
    {
        "category": "medium",
        "task_type": "explanation",
        "prompt": "Compare merge sort and quicksort: time complexity, space complexity, and when to use each.",
        "skill_level": "intermediate",
        "expected_model_tier": "standard",
    },
    {
        "category": "medium",
        "task_type": "socratic",
        "prompt": "Guide me to understand why linked lists use dynamic memory allocation.",
        "skill_level": "intermediate",
        "expected_model_tier": "standard",
    },
    {
        "category": "medium",
        "task_type": "code_example",
        "prompt": "Write a Python function implementing binary search with clear comments.",
        "skill_level": "intermediate",
        "expected_model_tier": "heavy",  # qwen2.5-coder
    },
    {
        "category": "medium",
        "task_type": "code_example",
        "prompt": "Implement a stack data structure in C with push, pop, and peek operations.",
        "skill_level": "intermediate",
        "expected_model_tier": "heavy",
    },
    {
        "category": "medium",
        "task_type": "quiz",
        "prompt": "Generate 5 multiple choice questions on object-oriented programming concepts.",
        "skill_level": "intermediate",
        "expected_model_tier": "standard",
    },
    # ── HARD ─────────────────────────────────────────────────────────────────
    {
        "category": "hard",
        "task_type": "roadmap",
        "prompt": "Generate a complete 8-week learning roadmap for mastering Python data structures and algorithms from beginner to interview-ready level.",
        "skill_level": "beginner",
        "expected_model_tier": "standard",  # high output_length + structured_output
    },
    {
        "category": "hard",
        "task_type": "roadmap",
        "prompt": "Create a comprehensive 10-week Java OOP course roadmap with weekly topics, exercises, projects, and assessment quizzes.",
        "skill_level": "intermediate",
        "expected_model_tier": "heavy",
    },
    {
        "category": "hard",
        "task_type": "explanation",
        "prompt": "Write a 2,000 word educational article on operating system scheduling algorithms: FCFS, SJF, Round Robin, Priority Scheduling. Include comparisons, examples, and diagrams described in text.",
        "skill_level": "advanced",
        "expected_model_tier": "heavy",
    },
    {
        "category": "hard",
        "task_type": "code_example",
        "prompt": "Implement a thread-safe LRU cache in Python using OrderedDict and threading.Lock with full unit tests.",
        "skill_level": "advanced",
        "expected_model_tier": "heavy",
    },
    {
        "category": "hard",
        "task_type": "explanation",
        "prompt": "Explain distributed consensus algorithms: Paxos, Raft, and Zab. Compare their fault tolerance, leader election, and log replication strategies.",
        "skill_level": "advanced",
        "expected_model_tier": "heavy",
    },
]


# ── Simulated responses for offline benchmarking ──────────────────────────────
# Replace these with actual Ollama responses when running live benchmarks.
SIMULATED_RESPONSES: Dict[str, str] = {
    "easy_explanation_0": "A variable is a named storage location in memory that holds a value. For example: x = 5 stores the integer 5 with the name 'x'.",
    "default": "# Simulated Response\n\nThis is a placeholder response used for offline benchmark testing.\n\n## Section 1\nContent here.\n\n## Section 2\nMore content here.\n\n- Point 1\n- Point 2\n- Point 3",
}


@dataclass
class BenchmarkResult:
    category: str
    task_type: str
    prompt_preview: str
    skill_level: str
    expected_tier: str
    selected_model: str
    selected_tier: str
    candidates_count: int
    candidates: List[str]
    routing_policy: str
    # Capability requirements
    complexity: float
    reasoning: float
    coding: float
    knowledge: float
    output_length: float
    # Quality evaluation
    quality_score: float
    quality_notes: List[str]
    # Tier match
    tier_correct: bool


def run_benchmark(verbose: bool = True) -> List[BenchmarkResult]:
    from app.router.registry import get_model_profile

    results: List[BenchmarkResult] = []

    for i, task in enumerate(BENCHMARK_TASKS):
        task_type = task["task_type"]
        prompt = task["prompt"]
        skill_level = task["skill_level"]

        # Route the task
        route = router_engine.route_task(
            task_type=task_type,
            prompt=prompt,
            user_skill_level=skill_level,
        )

        selected = route["selected_model"]
        selected_profile = get_model_profile(selected)
        features = route["features"]
        candidates = route["candidates"]

        # Get a simulated response for quality evaluation
        sim_key = f"{task['category']}_{task_type}_{i}"
        response_text = SIMULATED_RESPONSES.get(sim_key, SIMULATED_RESPONSES["default"])

        quality = evaluate_response(
            response_text=response_text,
            task_type=task_type,
            prompt=prompt,
            requires_json=task_type in ("roadmap", "quiz"),
            requires_code=task_type == "code_example",
        )

        tier_correct = selected_profile.tier == task["expected_model_tier"]

        result = BenchmarkResult(
            category=task["category"],
            task_type=task_type,
            prompt_preview=prompt[:60] + "..." if len(prompt) > 60 else prompt,
            skill_level=skill_level,
            expected_tier=task["expected_model_tier"],
            selected_model=selected,
            selected_tier=selected_profile.tier,
            candidates_count=len(candidates),
            candidates=[m for m, _ in candidates],
            routing_policy=route["routing_policy_used"],
            complexity=features.complexity,
            reasoning=features.reasoning_requirement,
            coding=features.coding_requirement,
            knowledge=features.knowledge_requirement,
            output_length=features.output_length_requirement,
            quality_score=quality.overall,
            quality_notes=quality.notes,
            tier_correct=tier_correct,
        )
        results.append(result)

        if verbose:
            status = "OK" if tier_correct else "!!"
            print(
                f"[{status}] [{task['category'].upper():6}] {task_type:12} "
                f"skill={skill_level:12} "
                f"-> {selected:20} (tier={selected_profile.tier:10}) "
                f"quality={quality.overall:.2f} "
                f"candidates={len(candidates)}"
            )

    return results


def print_summary(results: List[BenchmarkResult]) -> None:
    total = len(results)
    tier_correct = sum(1 for r in results if r.tier_correct)
    avg_quality = sum(r.quality_score for r in results) / total if total else 0
    avg_candidates = sum(r.candidates_count for r in results) / total if total else 0

    # Model distribution
    model_counts: Dict[str, int] = {}
    for r in results:
        model_counts[r.selected_model] = model_counts.get(r.selected_model, 0) + 1

    sep = "=" * 70
    print("\n" + sep)
    print("BENCHMARK SUMMARY")
    print(sep)
    print(f"  Total tasks:        {total}")
    print(f"  Tier-correct:       {tier_correct}/{total} ({100*tier_correct//total}%)")
    print(f"  Avg quality score:  {avg_quality:.3f}")
    print(f"  Avg candidates:     {avg_candidates:.1f}  (models passing filter)")
    print()
    print("  Model distribution:")
    for model, count in sorted(model_counts.items(), key=lambda x: -x[1]):
        bar = "#" * count
        print(f"    {model:25} {bar} ({count})")
    print()

    # Per-category breakdown
    for cat in ("easy", "medium", "hard"):
        cat_results = [r for r in results if r.category == cat]
        if not cat_results:
            continue
        cat_correct = sum(1 for r in cat_results if r.tier_correct)
        cat_quality = sum(r.quality_score for r in cat_results) / len(cat_results)
        print(
            f"  {cat.upper():6}: {cat_correct}/{len(cat_results)} tier-correct, "
            f"avg quality={cat_quality:.3f}"
        )

    print(sep)



if __name__ == "__main__":
    print("AdaptRoute Router Benchmark Suite")
    print("=" * 70)
    print(f"Running {len(BENCHMARK_TASKS)} benchmark tasks...\n")

    start = time.time()
    results = run_benchmark(verbose=True)
    elapsed = time.time() - start

    print_summary(results)
    print(f"\n  Total time: {elapsed:.2f}s (routing decisions only, no LLM calls)")

    # Save results
    output = [asdict(r) for r in results]
    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\n  Results saved to benchmark_results.json")
