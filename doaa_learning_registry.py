"""In-memory governed learning registry for Doaa.

The registry records explicit experiences and candidates. It does not train a
model, modify source code, call the network, or promote candidates implicitly.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

CONTRACT = "doaa.learning.v1"
_PROTOCOL = "doaa.alg.v1"
_CONSENTS = {"user_allowed", "public_source_reviewed", "not_allowed"}
_STATES = {"experience", "candidate", "active", "rejected", "revoked"}


class LearningRegistry:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}
        self._active_by_capability: dict[str, str] = {}

    def record_experience(self, record_id: Any, source: Any, created_at: Any, request: Any, result: Any, consent_status: Any) -> dict[str, Any]:
        if not self._identity_available(record_id):
            return _blocked("record_id_invalid")
        if record_id in self._records:
            return _blocked("record_id_exists")
        if not all(isinstance(value, str) and value.strip() for value in (source, created_at)):
            return _blocked("provenance_invalid")
        if consent_status not in _CONSENTS or consent_status == "not_allowed":
            return _blocked("consent_required")
        if not isinstance(request, dict) or not isinstance(result, dict):
            return _blocked("experience_payload_invalid")
        if request.get("protocol") not in {None, _PROTOCOL} or result.get("protocol") not in {None, _PROTOCOL}:
            return _blocked("protocol_invalid")
        payload = {"request": request, "result": result}
        normalized = {"record_id": record_id, "state": "experience", "source": source, "created_at": created_at, "content_digest": _digest(payload), "consent_status": consent_status, "protocol": _PROTOCOL, "authority": "none", "automatic_execution": False, "request": dict(request), "result": dict(result)}
        self._records[record_id] = normalized
        return _receipt("experience_recorded", record_id, state="experience")

    def propose_candidate(self, experience_id: Any, candidate_id: Any, capability: Any, algorithm_message: Any) -> dict[str, Any]:
        experience = self._records.get(experience_id)
        if experience is None or experience.get("state") != "experience":
            return _blocked("experience_not_found")
        if not self._identity_available(candidate_id) or candidate_id in self._records:
            return _blocked("candidate_id_invalid")
        if not isinstance(capability, str) or not capability.strip() or not isinstance(algorithm_message, dict) or algorithm_message.get("protocol") != _PROTOCOL:
            return _blocked("candidate_invalid")
        candidate = {"record_id": candidate_id, "state": "candidate", "source": f"experience:{experience_id}", "created_at": experience["created_at"], "content_digest": _digest(algorithm_message), "consent_status": experience["consent_status"], "protocol": _PROTOCOL, "authority": "none", "automatic_execution": False, "capability": capability, "algorithm_message": dict(algorithm_message), "experience_id": experience_id}
        self._records[candidate_id] = candidate
        return _receipt("candidate_proposed", candidate_id, state="candidate")

    def promote(self, candidate_id: Any, benchmark_receipt: Any, safety_receipt: Any, human_approval: Any) -> dict[str, Any]:
        candidate = self._records.get(candidate_id)
        if candidate is None or candidate.get("state") != "candidate":
            return _blocked("candidate_not_found")
        if not all(isinstance(value, dict) and value.get("status") == "passed" for value in (benchmark_receipt, safety_receipt)):
            return _blocked("evaluation_receipts_required")
        if human_approval is not True:
            return _blocked("human_approval_required")
        capability = candidate["capability"]
        previous = self._active_by_capability.get(capability)
        if previous:
            self._records[previous]["state"] = "revoked"
        candidate["state"] = "active"
        candidate["benchmark_receipt"] = dict(benchmark_receipt)
        candidate["safety_receipt"] = dict(safety_receipt)
        candidate["human_approval"] = True
        self._active_by_capability[capability] = candidate_id
        return _receipt("candidate_promoted", candidate_id, state="active", previous_active=previous)

    def revoke(self, record_id: Any, reason: Any) -> dict[str, Any]:
        record = self._records.get(record_id)
        if record is None or record.get("state") != "active":
            return _blocked("active_record_not_found")
        if not isinstance(reason, str) or not reason.strip():
            return _blocked("revoke_reason_required")
        record["state"] = "revoked"
        if self._active_by_capability.get(record.get("capability")) == record_id:
            del self._active_by_capability[record["capability"]]
        record["revoke_reason"] = reason
        return _receipt("active_record_revoked", record_id, state="revoked")

    def get_active(self, capability: Any) -> dict[str, Any]:
        record_id = self._active_by_capability.get(capability)
        if record_id is None:
            return _blocked("active_record_not_found")
        return {"status": "active_record_ready", "record": dict(self._records[record_id]), "execution_authority": "none", "automatic_execution": False}

    def export(self) -> dict[str, Any]:
        return {"contract": CONTRACT, "records": [dict(record) for record in self._records.values()], "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _identity_available(record_id: Any) -> bool:
        return isinstance(record_id, str) and bool(record_id.strip()) and len(record_id) <= 128


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _receipt(status: str, record_id: str, state: str, **extra: Any) -> dict[str, Any]:
    return {"status": status, "record_id": record_id, "state": state, **extra, "execution_authority": "none", "automatic_execution": False}


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "learning_operation_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
