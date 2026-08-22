"""
Router package — adaptive multi-LLM routing engine.
"""
from app.router.engine import router_engine, AdaptiveRouterEngine
from app.router.evaluator import evaluate_response, QualityReport
from app.router.feature_extractor import TaskFeatures, extract_features
from app.router.policies import CapabilityFilter
from app.router.registry import MODEL_REGISTRY, ModelCapabilities, get_model_profile

__all__ = [
    "router_engine",
    "AdaptiveRouterEngine",
    "CapabilityFilter",
    "evaluate_response",
    "QualityReport",
    "TaskFeatures",
    "extract_features",
    "MODEL_REGISTRY",
    "ModelCapabilities",
    "get_model_profile",
]
