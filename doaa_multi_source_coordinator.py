"""Deterministic coordinator for Doaa's governed multi-source flow.

This coordinator plans a route only. It does not fetch, call a model, execute,
or promote knowledge. External adapters may be invoked by an explicit outer
application after reviewing its result.
"""
from __future__ import annotations

from typing import Any

from doaa_algorithm_library import AlgorithmLibrary
from doaa_knowledge_registry import KnowledgeRegistry
from doaa_web_evidence import WebEvidenceStore

CONTRACT = "doaa.unified_flow.v1"


class MultiSourceCoordinator:
    def __init__(self, algorithms: AlgorithmLibrary, knowledge: KnowledgeRegistry | None = None, evidence: WebEvidenceStore | None = None) -> None:
        self.algorithms = algorithms
        self.knowledge = knowledge or KnowledgeRegistry()
        self.evidence = evidence or WebEvidenceStore()

    def prepare(self, request: Any, library: Any, algorithm_id: Any | None = None, source_request: Any | None = None, version: str | None = None, require_fresh_evidence: bool = False, evidence_ids: list[str] | None = None) -> dict[str, Any]:
        if not isinstance(request, dict):
            return self._blocked("invalid_request")
        logical = self.algorithms.get_library(library)
        if logical is None:
            return self._blocked("unknown_library")
        if algorithm_id is not None and source_request is not None:
            exact = logical.find_exact(algorithm_id, source_request)
            if exact["status"] == "library_match_found":
                return {"status": "route_local_algorithm", "contract": CONTRACT, "library": library, "payload": exact["entry"]["message"], "source": "algorithm_library", "execution_authority": "none", "automatic_execution": False}
        approved_records = self.evidence.list(status="approved")["records"]
        approved_ids = {record["evidence_id"] for record in approved_records}
        requested_ids = set(evidence_ids or [])
        if require_fresh_evidence and not requested_ids.intersection(approved_ids):
            return self._blocked("fresh_evidence_required")
        if algorithm_id is not None and version is not None:
            active = self.knowledge.resolve(algorithm_id, library, version)
            if active["status"] == "knowledge_active_match":
                return {"status": "route_active_knowledge", "contract": CONTRACT, "library": library, "payload": active["record"], "source": "knowledge_registry", "evidence_ids": list(active["record"]["evidence_ids"]), "execution_authority": "none", "automatic_execution": False}
        return {"status": "route_model_or_review", "contract": CONTRACT, "library": library, "reason": "no_active_exact_reuse", "requires_explicit_adapter": True, "requires_human_review_for_library_update": True, "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "unified_flow_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
