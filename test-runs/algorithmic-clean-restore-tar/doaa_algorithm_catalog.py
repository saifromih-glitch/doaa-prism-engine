"""Closed-world algorithm catalog for reusable mediation algorithms."""
from __future__ import annotations

from doaa_algorithmic_protocol import ALGORITHMS

CATALOG = {
    "answer.compose.v1": {"version": "1", "purpose": "compose a structured answer", "input_kind": "text", "execution": "model_only"},
    "answer.summarize.v1": {"version": "1", "purpose": "summarize text under explicit limits", "input_kind": "text", "execution": "model_only"},
    "task.plan.v1": {"version": "1", "purpose": "produce a non-executable task plan", "input_kind": "text", "execution": "model_only"},
}


def lookup(algorithm_id: str, version: str):
    record = CATALOG.get(algorithm_id)
    if not record or record["version"] != version:
        return {"status": "catalog_miss", "reason": "algorithm_not_registered", "execution_authority": "none", "automatic_execution": False}
    return {"status": "catalog_hit", "algorithm": {"id": algorithm_id, "version": version}, "definition": dict(record), "execution_authority": "none", "automatic_execution": False}


def list_registered():
    return [{"id": key, "version": value["version"]} for key, value in sorted(CATALOG.items())]


def propose_new_algorithm(candidate):
    """Return a governance proposal only; never mutates CATALOG."""
    return {"status": "governed_capability_request", "reason": "new_algorithm_requires_review", "candidate": candidate, "execution_authority": "none", "automatic_execution": False}
