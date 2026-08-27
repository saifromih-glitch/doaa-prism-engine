"""Deterministic local library for explicitly validated Doaa algorithms.

The library stores reusable algorithmic messages. It never infers a new
capability, performs semantic similarity search, calls a model, or executes a
stored message. Persistence is explicit and local.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROTOCOL = "doaa.alg.v1"
LIBRARY_CONTRACT = "doaa.algorithm_library.v1"


def request_fingerprint(request: Any) -> str:
    canonical = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AlgorithmLibrary:
    def __init__(self, entries: list[dict[str, Any]] | None = None) -> None:
        self._entries: dict[str, dict[str, Any]] = {}
        for entry in entries or []:
            self.register(entry)

    def register(self, entry: Any) -> dict[str, Any]:
        if not isinstance(entry, dict):
            return self._blocked("entry_not_object")
        required = {"entry_id", "algorithm_id", "protocol", "message", "source_request_fingerprint", "validation_status", "authority", "automatic_execution"}
        if set(entry) != required:
            return self._blocked("entry_schema_invalid")
        if not all(isinstance(entry[k], str) and entry[k].strip() for k in ("entry_id", "algorithm_id", "source_request_fingerprint")):
            return self._blocked("entry_identity_invalid")
        if entry["protocol"] != PROTOCOL or entry["validation_status"] != "validated":
            return self._blocked("entry_not_validated")
        if entry["authority"] != "none" or entry["automatic_execution"] is not False:
            return self._blocked("entry_authority_invalid")
        if not isinstance(entry["message"], dict) or entry["message"].get("protocol") != PROTOCOL:
            return self._blocked("message_invalid")
        if entry["entry_id"] in self._entries:
            return self._blocked("entry_id_exists")
        self._entries[entry["entry_id"]] = dict(entry)
        return {"status": "library_entry_registered", "entry_id": entry["entry_id"], "execution_authority": "none", "automatic_execution": False}

    def register_validated(self, algorithm_id: str, message: dict[str, Any], source_request: Any, entry_id: str) -> dict[str, Any]:
        """Explicit registration helper; caller is responsible for prior validation."""
        entry = {"entry_id": entry_id, "algorithm_id": algorithm_id, "protocol": PROTOCOL, "message": dict(message), "source_request_fingerprint": request_fingerprint(source_request), "validation_status": "validated", "authority": "none", "automatic_execution": False}
        return self.register(entry)

    def find_exact(self, algorithm_id: Any, source_request: Any) -> dict[str, Any]:
        fingerprint = request_fingerprint(source_request)
        matches = [e for e in self._entries.values() if e["algorithm_id"] == algorithm_id and e["source_request_fingerprint"] == fingerprint]
        if len(matches) == 1:
            return {"status": "library_match_found", "match_type": "exact", "entry": dict(matches[0]), "execution_authority": "none", "automatic_execution": False}
        if len(matches) > 1:
            return self._blocked("ambiguous_exact_match")
        return {"status": "library_miss", "reason": "exact_match_not_found", "execution_authority": "none", "automatic_execution": False}

    def export(self) -> dict[str, Any]:
        return {"contract": LIBRARY_CONTRACT, "entries": [dict(e) for e in self._entries.values()], "execution_authority": "none", "automatic_execution": False}

    def save(self, path: str | Path) -> dict[str, Any]:
        Path(path).write_text(json.dumps(self.export(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"status": "library_saved", "entry_count": len(self._entries), "execution_authority": "none", "automatic_execution": False}

    @classmethod
    def load(cls, path: str | Path) -> "AlgorithmLibrary":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("contract") != LIBRARY_CONTRACT or data.get("execution_authority") != "none" or data.get("automatic_execution") is not False:
            raise ValueError("library_contract_invalid")
        return cls(data.get("entries", []))

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "library_operation_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
