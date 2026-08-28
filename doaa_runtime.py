"""Doaa Runtime v1: local-first, governed route preparation.

The runtime composes existing stores and returns a reviewed route. It never
calls a model, fetches the web, executes tools, promotes knowledge, or edits
source code.
"""
from __future__ import annotations

from typing import Any

from doaa_command_language import parse_command
from doaa_multi_source_coordinator import MultiSourceCoordinator
from doaa_reuse_ledger import ReuseLedger
from doaa_template_reconstruction import TemplateRegistry
from doaa_context_extractor import extract_supported_answer

CONTRACT = "doaa.runtime.v1"


class DoaaRuntime:
    def __init__(self, coordinator: MultiSourceCoordinator, templates: TemplateRegistry | None = None, reuse_ledger: ReuseLedger | None = None) -> None:
        self.coordinator = coordinator
        self.templates = templates or TemplateRegistry()
        self.reuse_ledger = reuse_ledger or ReuseLedger()

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
        self.reuse_ledger.observe(route["status"])
        return {"status": "runtime_ready" if route["status"] in {"route_local_algorithm", "route_active_knowledge", "route_model_or_review"} else "runtime_blocked", "contract": CONTRACT, "route": route, "reuse": self.reuse_ledger.stats(), "next_action": "use_local_payload" if route["status"] == "route_local_algorithm" else "explicit_adapter_or_human_review", "execution_authority": "none", "automatic_execution": False}

    def prepare_reconstruction(self, template_id: Any, slots: Any) -> dict[str, Any]:
        rebuilt = self.templates.reconstruct(template_id, slots)
        if rebuilt["status"] != "reconstruction_ready":
            return {"status": "runtime_blocked" if rebuilt["status"] == "reconstruction_blocked" else "runtime_governed_review", "reconstruction": rebuilt, "execution_authority": "none", "automatic_execution": False}
        envelope = {"request": rebuilt["request"], "library": rebuilt["library"], "algorithm_id": rebuilt["algorithm_id"], "source_request": rebuilt["request"]}
        result = self.prepare(envelope)
        result["reconstruction"] = rebuilt
        return result

    def prepare_local_answer(self, question: Any, context: Any) -> dict[str, Any]:
        result = extract_supported_answer(question, context)
        if result["status"] != "candidate":
            return {"status": "runtime_governed_review", "local_answer": result, "next_action": "explicit_adapter_or_human_review", "execution_authority": "none", "automatic_execution": False}
        return {"status": "runtime_local_candidate", "local_answer": result, "next_action": "verify_against_source_before_delivery", "execution_authority": "none", "automatic_execution": False}

    def prepare_command(self, command: Any) -> dict[str, Any]:
        parsed = parse_command(command)
        if parsed["status"] != "command_parsed":
            return {"status": "runtime_blocked" if parsed["status"] == "command_blocked" else "runtime_governed_review", "contract": CONTRACT, "command": parsed, "execution_authority": "none", "automatic_execution": False}
        request = {"command": parsed["command"], "capability": parsed["capability"], "slots": parsed["slots"]}
        envelope = {"request": request, "library": parsed["library"], "algorithm_id": f"{parsed['capability']}.v1", "source_request": request}
        result = self.prepare(envelope)
        result["command"] = parsed
        return result

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "runtime_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
