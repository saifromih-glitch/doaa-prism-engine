"""Governed distillation: propose reusable algorithms without mutating state."""
from __future__ import annotations

from collections import Counter
from typing import Any

FORBIDDEN = {"shell", "subprocess", "source_code", "generated_code", "tool_call", "write_path", "credentials", "secret_access", "model_update", "self_update"}


def _safe_record(record: Any) -> bool:
    return isinstance(record, dict) and record.get("status") == "accepted" and record.get("execution_authority") == "none" and record.get("automatic_execution") is False and isinstance(record.get("algorithm"), dict) and not FORBIDDEN.intersection(record)


def propose_distillation(records: Any, minimum_support: int = 3) -> dict[str, Any]:
    if not isinstance(records, list) or not isinstance(minimum_support, int) or minimum_support < 2:
        return {"status": "distillation_blocked", "reason": "input_invalid", "execution_authority": "none", "automatic_execution": False}
    if any(not _safe_record(record) for record in records):
        return {"status": "distillation_blocked", "reason": "unaccepted_record_present", "execution_authority": "none", "automatic_execution": False}
    keys = [(r["algorithm"].get("id"), r["algorithm"].get("version")) for r in records]
    counts = Counter(keys)
    if not counts:
        return {"status": "distillation_blocked", "reason": "insufficient_support", "execution_authority": "none", "automatic_execution": False}
    key, count = counts.most_common(1)[0]
    if count < minimum_support:
        return {"status": "distillation_blocked", "reason": "insufficient_support", "execution_authority": "none", "automatic_execution": False}
    return {"status": "distillation_candidate", "candidate": {"algorithm": {"id": key[0], "version": key[1]}, "support": count, "required_review": True, "library_mutation": False, "model_update": False}, "execution_authority": "none", "automatic_execution": False}
