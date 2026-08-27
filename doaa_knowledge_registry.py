"""Governed registry for reusable Doaa capabilities and knowledge templates.

The registry is deliberately explicit: proposals can be recorded, but only a
human approval event can promote one to active. It does not execute, call a
model, fetch the web, or modify source code.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT = "doaa.knowledge_registry.v1"
STATUSES = {"pending_review", "active", "expired", "revoked"}
LIBRARIES = {"science", "industry", "software", "business", "marketing", "sales", "education", "language", "general"}


class KnowledgeRegistry:
    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self._records: dict[str, dict[str, Any]] = {}
        for record in records or []:
            result = self.register(record)
            if result.get("status") != "knowledge_registered":
                raise ValueError(result.get("reason", "knowledge_invalid"))

    def register(self, record: Any) -> dict[str, Any]:
        required = {"record_id", "algorithm_id", "library", "version", "status", "evidence_ids", "input_schema", "output_schema"}
        if not isinstance(record, dict) or not required.issubset(record):
            return self._blocked("record_schema_invalid")
        if not isinstance(record["record_id"], str) or not record["record_id"].strip() or record["record_id"] in self._records:
            return self._blocked("record_identity_invalid")
        if not isinstance(record["algorithm_id"], str) or not record["algorithm_id"].strip() or record["library"] not in LIBRARIES or not isinstance(record["version"], str) or not record["version"].strip():
            return self._blocked("record_scope_invalid")
        if record["status"] not in STATUSES or not isinstance(record["evidence_ids"], list) or not all(isinstance(x, str) and x.strip() for x in record["evidence_ids"]):
            return self._blocked("record_status_or_evidence_invalid")
        if not isinstance(record["input_schema"], dict) or not isinstance(record["output_schema"], dict):
            return self._blocked("record_schema_invalid")
        normalized = dict(record)
        normalized.update({"execution_authority": "none", "automatic_execution": False, "automatic_promotion": False})
        self._records[record["record_id"]] = normalized
        return {"status": "knowledge_registered", "record_id": record["record_id"], "review_status": record["status"], "execution_authority": "none", "automatic_execution": False}

    def propose(self, record: dict[str, Any]) -> dict[str, Any]:
        candidate = dict(record)
        candidate["status"] = "pending_review"
        result = self.register(candidate)
        if result.get("status") != "knowledge_registered":
            return result
        return {"status": "knowledge_proposal_recorded", "record_id": candidate["record_id"], "requires_human_approval": True, "automatic_promotion": False, "execution_authority": "none", "automatic_execution": False}

    def promote(self, record_id: Any, reviewer: str) -> dict[str, Any]:
        if not isinstance(reviewer, str) or not reviewer.strip():
            return self._blocked("reviewer_required")
        record = self._records.get(record_id)
        if record is None:
            return self._blocked("record_not_found")
        if record["status"] != "pending_review":
            return self._blocked("record_not_pending")
        updated = dict(record)
        updated.update({"status": "active", "approved_by": reviewer, "automatic_promotion": False})
        self._records[record_id] = updated
        return {"status": "knowledge_promoted", "record_id": record_id, "approved_by": reviewer, "automatic_promotion": False, "execution_authority": "none", "automatic_execution": False}

    def resolve(self, algorithm_id: Any, library: Any, version: Any) -> dict[str, Any]:
        matches = [dict(r) for r in self._records.values() if r["algorithm_id"] == algorithm_id and r["library"] == library and r["version"] == version and r["status"] == "active"]
        if len(matches) == 1:
            return {"status": "knowledge_active_match", "record": matches[0], "execution_authority": "none", "automatic_execution": False}
        if len(matches) > 1:
            return self._blocked("ambiguous_active_match")
        return {"status": "knowledge_miss", "reason": "active_exact_record_not_found", "execution_authority": "none", "automatic_execution": False}

    def list(self, library: str | None = None, status: str | None = None) -> dict[str, Any]:
        if library is not None and library not in LIBRARIES:
            return self._blocked("library_unknown")
        if status is not None and status not in STATUSES:
            return self._blocked("status_unknown")
        records = [dict(r) for r in self._records.values() if (library is None or r["library"] == library) and (status is None or r["status"] == status)]
        records.sort(key=lambda r: r["record_id"])
        return {"status": "knowledge_list_ready", "count": len(records), "records": records, "execution_authority": "none", "automatic_execution": False}

    def save(self, path: str | Path) -> dict[str, Any]:
        Path(path).write_text(json.dumps({"contract": CONTRACT, "records": list(self._records.values()), "execution_authority": "none", "automatic_execution": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"status": "knowledge_registry_saved", "record_count": len(self._records), "execution_authority": "none", "automatic_execution": False}

    @classmethod
    def load(cls, path: str | Path) -> "KnowledgeRegistry":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("contract") != CONTRACT or data.get("execution_authority") != "none" or data.get("automatic_execution") is not False:
            raise ValueError("knowledge_registry_contract_invalid")
        return cls(data.get("records", []))

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "knowledge_operation_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
