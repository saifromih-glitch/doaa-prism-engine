"""Doaa Runtime v1: local-first, governed route preparation.

The runtime composes existing stores and returns a reviewed route. It never
calls a model, fetches the web, executes tools, promotes knowledge, or edits
source code.
"""
from __future__ import annotations

from typing import Any

from doaa_multi_source_coordinator import MultiSourceCoordinator

CONTRACT = "doaa.runtime.v1"


class DoaaRuntime:
    def __init__(self, coordinator: MultiSourceCoordinator) -> None:
        self.coordinator = coordinator

    def prepare(self, envelope: Any) -> dict[str, Any]:
        if not isinstance(envelope, dict):
            return self._blocked("invalid_envelope")
        allowed = {"request", "library", "algorithm_id", "source_request", "version", "require_fresh_evidence", "evidence_ids"}
        if set(envelope) - allowed:
            return self._blocked("envelope_keys_not_allowed")
        if not isinstance(envelope.get("request"), dict) or not isinstance(envelope.get("library"), str):
            return self._blocked("request_or_library_invalid")
        route = self.coordinator.prepare(
            request=envelope["request"],
            library=envelope["library"],
            algorithm_id=envelope.get("algorithm_id"),
            source_request=envelope.get("source_request"),
            version=envelope.get("version"),
            require_fresh_evidence=envelope.get("require_fresh_evidence", False),
            evidence_ids=envelope.get("evidence_ids", []),
        )
        return {"status": "runtime_ready" if route["status"] in {"route_local_algorithm", "route_active_knowledge", "route_model_or_review"} else "runtime_blocked", "contract": CONTRACT, "route": route, "next_action": "use_local_payload" if route["status"] == "route_local_algorithm" else "explicit_adapter_or_human_review", "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "runtime_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
