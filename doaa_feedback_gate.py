"""Deterministic gate connecting human feedback to learning candidates."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.feedback_gate.v1"


def assess_feedback_for_candidate(feedback_signal: Any, candidate_id: Any, independent_truth: Any = "unverified") -> dict[str, Any]:
    if not isinstance(feedback_signal, dict) or feedback_signal.get("status") != "learning_signal_ready":
        return _blocked("learning_signal_required")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        return _blocked("candidate_id_invalid")
    if independent_truth not in {"unverified", "verified_true", "verified_false"}:
        return _blocked("independent_truth_invalid")
    negative = bool(feedback_signal.get("negative_signal"))
    correctness = feedback_signal.get("correctness_signal")
    truth_verified = independent_truth != "unverified"
    correctness_support = independent_truth == "verified_true" and correctness == "believed_true"
    correctness_block = independent_truth == "verified_false" or correctness == "believed_false"
    eligible = not negative and not correctness_block and (correctness == "unknown" or correctness_support or not feedback_signal.get("requires_independent_evidence", False))
    return {
        "status": "feedback_supports_candidate" if eligible else "feedback_blocks_candidate",
        "contract": CONTRACT,
        "candidate_id": candidate_id,
        "usefulness_signal": feedback_signal["usefulness_score"],
        "correctness_signal": correctness,
        "independent_truth": independent_truth,
        "truth_verified": truth_verified,
        "promotion_eligible": False,
        "candidate_learning_eligible": eligible,
        "reason": "human_feedback_is_signal_only" if eligible else ("independent_evidence_conflict" if correctness_block else "negative_or_unverified_feedback"),
        "requires_human_review": True,
        "execution_authority": "none",
        "automatic_execution": False,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "feedback_gate_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
