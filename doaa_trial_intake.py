"""Validate consented human-trial records; never invent participant feedback."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.72h_trial_intake.v1"


def validate_trial_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        return _blocked("record_object_required")
    required = ("participant_id", "consent_feedback", "real_task", "problem_present", "would_retry")
    if any(key not in record for key in required):
        return _blocked("required_field_missing")
    if not isinstance(record["participant_id"], str) or not record["participant_id"].strip():
        return _blocked("anonymous_participant_id_required")
    if not isinstance(record["consent_feedback"], bool) or not isinstance(record["real_task"], bool):
        return _blocked("boolean_consent_and_real_task_required")
    if not record["real_task"]:
        return _blocked("synthetic_or_hypothetical_task_rejected")
    if not isinstance(record["problem_present"], bool) or not isinstance(record["would_retry"], bool):
        return _blocked("boolean_trial_fields_required")
    if record["consent_feedback"] and "feedback" in record and not isinstance(record["feedback"], str):
        return _blocked("feedback_must_be_text")
    return {"status": "trial_record_accepted", "contract": CONTRACT, "participant_id": record["participant_id"], "problem_present": record["problem_present"], "would_retry": record["would_retry"], "feedback_collected": record["consent_feedback"] and "feedback" in record, "learning_consent": bool(record.get("consent_learning", False)), "execution_authority": "none", "automatic_execution": False}


def summarize(records: list[Any]) -> dict[str, Any]:
    validated = [validate_trial_record(record) for record in records]
    accepted = [record for record in validated if record["status"] == "trial_record_accepted"]
    return {"status": "trial_summary", "submitted": len(records), "accepted": len(accepted), "problem_count": sum(record["problem_present"] for record in accepted), "retry_count": sum(record["would_retry"] for record in accepted), "success_threshold_met": sum(record["problem_present"] for record in accepted) >= 3 and sum(record["would_retry"] for record in accepted) >= 2, "synthetic_records_included": False, "execution_authority": "none", "automatic_execution": False}


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "trial_record_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
