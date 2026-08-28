"""Bounded human feedback for Doaa learning signals."""
from __future__ import annotations

import hashlib
import json
from typing import Any

CONTRACT = "doaa.feedback.v1"
_CORRECTNESS = {"unknown", "believed_true", "believed_false", "needs_verification"}


class FeedbackStore:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def submit(self, feedback: Any) -> dict[str, Any]:
        if not isinstance(feedback, dict):
            return _blocked("feedback_must_be_object")
        required = {"feedback_id", "interaction_id", "usefulness", "correctness_signal", "consent_to_learning", "created_at"}
        allowed = required | {"correction", "reason"}
        if set(feedback) - allowed or not required.issubset(feedback):
            return _blocked("feedback_schema_invalid")
        if not _valid_id(feedback["feedback_id"]) or not _valid_id(feedback["interaction_id"]):
            return _blocked("feedback_identity_invalid")
        if feedback["feedback_id"] in self._records:
            return _blocked("feedback_id_exists")
        if not isinstance(feedback["usefulness"], int) or not 1 <= feedback["usefulness"] <= 5:
            return _blocked("usefulness_invalid")
        if feedback["correctness_signal"] not in _CORRECTNESS:
            return _blocked("correctness_signal_invalid")
        if not isinstance(feedback["consent_to_learning"], bool) or not isinstance(feedback["created_at"], str) or not feedback["created_at"].strip():
            return _blocked("consent_or_timestamp_invalid")
        for field in ("correction", "reason"):
            if field in feedback and (not isinstance(feedback[field], str) or len(feedback[field]) > 2000):
                return _blocked(f"{field}_invalid")
        normalized = dict(feedback)
        normalized.update({"contract": CONTRACT, "record_digest": _digest(feedback), "identity_collected": False, "execution_authority": "none", "automatic_execution": False})
        self._records[feedback["feedback_id"]] = normalized
        return {"status": "feedback_recorded", "feedback_id": feedback["feedback_id"], "learning_eligible": feedback["consent_to_learning"], "execution_authority": "none", "automatic_execution": False}

    def assess_learning_signal(self, feedback_id: Any) -> dict[str, Any]:
        record = self._records.get(feedback_id)
        if record is None:
            return _blocked("feedback_not_found")
        if not record["consent_to_learning"]:
            return {"status": "learning_signal_blocked", "reason": "consent_not_granted", "feedback_id": feedback_id, "execution_authority": "none", "automatic_execution": False}
        correctness = record["correctness_signal"]
        return {"status": "learning_signal_ready", "feedback_id": feedback_id, "usefulness_score": record["usefulness"], "correctness_signal": correctness, "truth_verified": False, "requires_independent_evidence": correctness != "unknown", "negative_signal": correctness == "believed_false" or record["usefulness"] <= 2, "execution_authority": "none", "automatic_execution": False}

    def delete(self, feedback_id: Any) -> dict[str, Any]:
        if feedback_id not in self._records:
            return _blocked("feedback_not_found")
        del self._records[feedback_id]
        return {"status": "feedback_deleted", "feedback_id": feedback_id, "execution_authority": "none", "automatic_execution": False}

    def export(self) -> dict[str, Any]:
        return {"contract": CONTRACT, "records": [dict(item) for item in self._records.values()], "execution_authority": "none", "automatic_execution": False}


def _valid_id(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 128


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "feedback_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
