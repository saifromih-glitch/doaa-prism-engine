"""Deterministic multi-dimensional confidence signals for Doaa."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.confidence.v1"


def score_signals(usefulness: Any, correctness_signal: Any, safety_pass: Any, baseline_tokens: Any, compact_tokens: Any, evidence_status: Any = "unverified") -> dict[str, Any]:
    if not isinstance(usefulness, int) or not 1 <= usefulness <= 5:
        return _blocked("usefulness_invalid")
    if correctness_signal not in {"unknown", "believed_true", "believed_false", "needs_verification"}:
        return _blocked("correctness_signal_invalid")
    if not isinstance(safety_pass, bool):
        return _blocked("safety_invalid")
    if not isinstance(baseline_tokens, int) or not isinstance(compact_tokens, int) or baseline_tokens <= 0 or compact_tokens < 0:
        return _blocked("token_metrics_invalid")
    if evidence_status not in {"unverified", "verified_true", "verified_false"}:
        return _blocked("evidence_status_invalid")
    usefulness_score = round(usefulness / 5, 4)
    token_saving_ratio = round((baseline_tokens - compact_tokens) / baseline_tokens, 4)
    if correctness_signal == "unknown":
        correctness_score = None
    elif correctness_signal == "believed_false" or evidence_status == "verified_false":
        correctness_score = 0.0
    elif correctness_signal == "believed_true" and evidence_status == "verified_true":
        correctness_score = 1.0
    else:
        correctness_score = None
    return {
        "status": "confidence_signals_ready",
        "contract": CONTRACT,
        "usefulness_score": usefulness_score,
        "correctness_score": correctness_score,
        "correctness_is_verified": correctness_score is not None and evidence_status == "verified_true",
        "safety_score": 1.0 if safety_pass else 0.0,
        "token_saving_ratio": token_saving_ratio,
        "quality_for_promotion": usefulness_score >= 0.8 and safety_pass and token_saving_ratio > 0 and correctness_score != 0.0,
        "truth_claim": "not_established" if correctness_score is None else ("supported_by_evidence" if correctness_score == 1.0 else "contradicted"),
        "execution_authority": "none",
        "automatic_execution": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "confidence_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
