"""Local, provenance-first web evidence store for Doaa.

This module stores evidence records only. It does not fetch the web, interpret
embedded instructions, update algorithm libraries, call models, or execute.
A separate explicit connector may provide fetched records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

CONTRACT = "doaa.web_evidence.v1"
STATUSES = {"pending_review", "approved", "rejected", "expired"}
DOMAINS = {"science", "industry", "software", "business", "education", "language", "general"}


def content_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _valid_url(value: Any) -> bool:
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.netloc and len(value) <= 2048)


class WebEvidenceStore:
    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self._records: dict[str, dict[str, Any]] = {}
        for record in records or []:
            result = self.add(record)
            if result.get("status") != "evidence_registered":
                raise ValueError(result.get("reason", "evidence_invalid"))

    def add(self, record: Any) -> dict[str, Any]:
        if not isinstance(record, dict):
            return self._blocked("record_not_object")
        required = {"evidence_id", "source_url", "source_title", "retrieved_at", "content_digest", "claim", "evidence_span", "domain", "status"}
        if not required.issubset(record):
            return self._blocked("provenance_fields_missing")
        if not isinstance(record["evidence_id"], str) or not record["evidence_id"].strip() or record["evidence_id"] in self._records:
            return self._blocked("evidence_identity_invalid")
        if not _valid_url(record["source_url"]):
            return self._blocked("invalid_url")
        if not all(isinstance(record[k], str) and record[k].strip() for k in ("source_title", "retrieved_at", "content_digest", "claim", "evidence_span")):
            return self._blocked("evidence_content_missing")
        if record["domain"] not in DOMAINS or record["status"] not in STATUSES:
            return self._blocked("domain_or_status_invalid")
        if len(record["claim"]) > 4000 or len(record["evidence_span"]) > 12000:
            return self._blocked("evidence_size_exceeded")
        normalized = dict(record)
        normalized["source_data_is_untrusted"] = True
        normalized["automatic_library_update"] = False
        self._records[record["evidence_id"]] = normalized
        return {"status": "evidence_registered", "evidence_id": record["evidence_id"], "review_status": record["status"], "execution_authority": "none", "automatic_execution": False}

    def approve(self, evidence_id: Any) -> dict[str, Any]:
        record = self._records.get(evidence_id)
        if record is None:
            return self._blocked("evidence_not_found")
        updated = dict(record)
        updated["status"] = "approved"
        self._records[evidence_id] = updated
        return {"status": "evidence_approved", "evidence_id": evidence_id, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}

    def list(self, domain: str | None = None, status: str | None = None) -> dict[str, Any]:
        if domain is not None and domain not in DOMAINS:
            return self._blocked("domain_unknown")
        if status is not None and status not in STATUSES:
            return self._blocked("status_unknown")
        records = [dict(r) for r in self._records.values() if (domain is None or r["domain"] == domain) and (status is None or r["status"] == status)]
        records.sort(key=lambda r: r["evidence_id"])
        return {"status": "evidence_list_ready", "count": len(records), "records": records, "execution_authority": "none", "automatic_execution": False}

    def propose_library_update(self, evidence_ids: list[str], library: str, rationale: str) -> dict[str, Any]:
        if not isinstance(evidence_ids, list) or not evidence_ids or not all(eid in self._records and self._records[eid]["status"] == "approved" for eid in evidence_ids):
            return self._blocked("approved_evidence_required")
        if not isinstance(library, str) or not library.strip() or not isinstance(rationale, str) or not rationale.strip():
            return self._blocked("proposal_fields_invalid")
        return {"status": "library_update_proposed", "library": library, "evidence_ids": list(evidence_ids), "rationale": rationale, "requires_human_approval": True, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}

    def export(self) -> dict[str, Any]:
        return {"contract": CONTRACT, "records": [dict(r) for r in self._records.values()], "execution_authority": "none", "automatic_execution": False}

    def save(self, path: str | Path) -> dict[str, Any]:
        Path(path).write_text(json.dumps(self.export(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"status": "evidence_store_saved", "record_count": len(self._records), "execution_authority": "none", "automatic_execution": False}

    @classmethod
    def load(cls, path: str | Path) -> "WebEvidenceStore":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("contract") != CONTRACT or data.get("execution_authority") != "none" or data.get("automatic_execution") is not False:
            raise ValueError("evidence_contract_invalid")
        return cls(data.get("records", []))

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "evidence_operation_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
