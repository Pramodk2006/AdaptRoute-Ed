"""
Multi-LLM Capability Registry — defines known models with full capability profiles.

Each model's capabilities are scored 0.0–1.0. These scores are used by the
CapabilityFilter to determine which models can actually satisfy a given task's
requirements before the LinUCB bandit makes its selection.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelCapabilities:
    """What a model is good at, scored 0.0 (poor) → 1.0 (excellent)."""
    reasoning: float          # multi-step logical reasoning
    coding: float             # code generation and debugging
    knowledge: float          # factual accuracy and breadth
    long_context: float       # handling long input contexts
    long_generation: float    # generating long, coherent outputs
    structured_output: float  # JSON / structured format compliance
    accuracy: float           # factual precision
    creativity: float         # narrative, explanation quality
    # Hardware / cost profile
    vram_mb: int              # approximate VRAM footprint (MB)
    speed_score: float        # 0.0 (slow) → 1.0 (very fast)


@dataclass
class ModelProfile:
    model_id: str
    display_name: str
    provider: str              # ollama | huggingface
    tier: str                  # lightweight | standard | heavy
    capabilities: ModelCapabilities
    cost_per_1k_input: float   # USD (0.0 for local models)
    cost_per_1k_output: float  # USD (0.0 for local models)
    avg_latency_ms: int


MODEL_REGISTRY: Dict[str, ModelProfile] = {
    # ── Gemma 3 1B — lightweight / fast ──────────────────────────────────────
    "gemma3:1b": ModelProfile(
        model_id="gemma3:1b",
        display_name="Gemma 3 1B (Fast)",
        provider="ollama",
        tier="lightweight",
        capabilities=ModelCapabilities(
            reasoning=0.45,
            coding=0.38,
            knowledge=0.48,
            long_context=0.35,
            long_generation=0.35,
            structured_output=0.65,
            accuracy=0.48,
            creativity=0.45,
            vram_mb=900,
            speed_score=0.95,
        ),
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=250,
    ),

    # ── Gemma 3 (4B/latest) — default standard ───────────────────────────────
    "gemma3:latest": ModelProfile(
        model_id="gemma3:latest",
        display_name="Gemma 3 4B (Default)",
        provider="ollama",
        tier="standard",
        capabilities=ModelCapabilities(
            reasoning=0.70,
            coding=0.65,
            knowledge=0.75,
            long_context=0.70,
            long_generation=0.65,
            structured_output=0.85,
            accuracy=0.72,
            creativity=0.70,
            vram_mb=4096,
            speed_score=0.55,
        ),
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=1200,
    ),

    # Keep bare "gemma3" as alias for gemma3:latest
    "gemma3": ModelProfile(
        model_id="gemma3",
        display_name="Gemma 3 (Default alias)",
        provider="ollama",
        tier="standard",
        capabilities=ModelCapabilities(
            reasoning=0.70,
            coding=0.65,
            knowledge=0.75,
            long_context=0.70,
            long_generation=0.65,
            structured_output=0.85,
            accuracy=0.72,
            creativity=0.70,
            vram_mb=4096,
            speed_score=0.55,
        ),
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=1200,
    ),

    # ── Llama 3.1 8B — strong reasoning ──────────────────────────────────────
    "llama3.1:8b": ModelProfile(
        model_id="llama3.1:8b",
        display_name="Llama 3.1 8B (Reasoning)",
        provider="ollama",
        tier="heavy",
        capabilities=ModelCapabilities(
            reasoning=0.82,
            coding=0.78,
            knowledge=0.80,
            long_context=0.80,
            long_generation=0.75,
            structured_output=0.80,
            accuracy=0.80,
            creativity=0.70,
            vram_mb=5000,
            speed_score=0.45,
        ),
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=1600,
    ),

    # ── Qwen 2.5 Coder — coding specialist ───────────────────────────────────
    "qwen2.5-coder": ModelProfile(
        model_id="qwen2.5-coder",
        display_name="Qwen 2.5 Coder (Code Expert)",
        provider="ollama",
        tier="heavy",
        capabilities=ModelCapabilities(
            reasoning=0.80,
            coding=0.95,
            knowledge=0.75,
            long_context=0.80,
            long_generation=0.75,
            structured_output=0.90,
            accuracy=0.82,
            creativity=0.50,
            vram_mb=5500,
            speed_score=0.40,
        ),
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=1800,
    ),
}


def get_model_profile(model_id: str) -> ModelProfile:
    """Retrieve model profile; falls back to gemma3:latest for unknown models."""
    return MODEL_REGISTRY.get(model_id) or MODEL_REGISTRY.get(
        "gemma3:latest", MODEL_REGISTRY["gemma3"]
    )
