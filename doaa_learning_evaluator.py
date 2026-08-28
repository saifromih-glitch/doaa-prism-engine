"""Deterministic evaluation gates for Doaa learning candidates."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.learning_eval.v1"
_MIN_QUALITY = 0.90


def evaluate_candidate(metrics: Any) -> dict[str, Any]:
    if not isinstance(metrics, dict):
        return _blocked("metrics_must_be_object")
    required = {"baseline_tokens", "compact_tokens", "quality_score", "safety_pass"}
    if set(metrics) - required or not required.issubset(metrics):
        return _blocked("metrics_schema_invalid")
    baseline = metrics["baseline_tokens"]
    compact = metrics["compact_tokens"]
    quality = metrics["quality_score"]
    safety = metrics["safety_pass"]
    if not isinstance(baseline, int) or not isinstance(compact, int) or baseline <= 0 or compact < 0:
        return _blocked("token_metrics_invalid")
    if not isinstance(quality, (int, float)) or not 0 <= quality <= 1:
        return _blocked("quality_metric_invalid")
    if not isinstance(safety, bool):
        return _blocked("safety_metric_invalid")
    saving = baseline - compact
    saving_ratio = saving / baseline
    passed = compact < baseline and quality >= _MIN_QUALITY and safety
    return {
        "status": "passed" if passed else "failed",
        "contract": CONTRACT,
        "baseline_tokens": baseline,
        "compact_tokens": compact,
        "token_saving": saving,
        "token_saving_ratio": round(saving_ratio, 6),
        "quality_score": quality,
        "safety_pass": safety,
        "minimum_quality": _MIN_QUALITY,
        "promotion_eligible": passed,
        "execution_authority": "none",
        "automatic_execution": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "evaluation_blocked", "contract": CONTRACT, "reason": reason, "promotion_eligible": False, "execution_authority": "none", "automatic_execution": False}
