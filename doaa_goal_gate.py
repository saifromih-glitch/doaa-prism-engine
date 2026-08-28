"""Deterministic acceptance gate for Doaa's primary token-saving goal."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.goal_gate.v1"


def assess_optimization(metrics: Any) -> dict[str, Any]:
    if not isinstance(metrics, dict):
        return _blocked("metrics_must_be_object")
    required = {"baseline_tokens", "doaa_tokens", "baseline_quality", "doaa_quality", "baseline_safety", "doaa_safety", "sample_count"}
    if set(metrics) - required or not required.issubset(metrics):
        return _blocked("metrics_schema_invalid")
    integer_fields = ("baseline_tokens", "doaa_tokens", "sample_count")
    if not all(isinstance(metrics[field], int) and metrics[field] >= 0 for field in integer_fields) or metrics["baseline_tokens"] <= 0 or metrics["sample_count"] < 1:
        return _blocked("count_metric_invalid")
    score_fields = ("baseline_quality", "doaa_quality")
    if not all(isinstance(metrics[field], (int, float)) and 0 <= metrics[field] <= 1 for field in score_fields):
        return _blocked("quality_metric_invalid")
    if not isinstance(metrics["baseline_safety"], bool) or not isinstance(metrics["doaa_safety"], bool):
        return _blocked("safety_metric_invalid")
    token_saving = metrics["baseline_tokens"] - metrics["doaa_tokens"]
    quality_delta = metrics["doaa_quality"] - metrics["baseline_quality"]
    safety_ok = metrics["doaa_safety"] and (metrics["baseline_safety"] is False or metrics["doaa_safety"] is True)
    passed = token_saving > 0 and quality_delta >= 0 and safety_ok
    return {
        "status": "goal_gate_passed" if passed else "goal_gate_failed",
        "contract": CONTRACT,
        "sample_count": metrics["sample_count"],
        "token_saving": token_saving,
        "token_saving_ratio": round(token_saving / metrics["baseline_tokens"], 6),
        "quality_delta": round(quality_delta, 6),
        "safety_preserved": safety_ok,
        "local_exact_reuse_preferred": True,
        "human_review_required": True,
        "automatic_active_promotion": False,
        "execution_authority": "none",
        "automatic_execution": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "goal_gate_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
