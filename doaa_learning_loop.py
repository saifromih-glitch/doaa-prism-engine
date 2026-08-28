"""Governed automatic learning loop for Doaa.

The loop may record consented experience and create a candidate when the
quality, safety, and token-saving gates pass. It never promotes the candidate.
"""
from __future__ import annotations

from typing import Any

from doaa_learning_evaluator import evaluate_candidate
from doaa_learning_registry import LearningRegistry

CONTRACT = "doaa.learning_loop.v1"


class GovernedLearningLoop:
    def __init__(self, registry: LearningRegistry | None = None) -> None:
        self.registry = registry or LearningRegistry()

    def observe_and_propose(self, record_id: Any, source: Any, created_at: Any, request: Any, result: Any, consent_status: Any, candidate_id: Any, capability: Any, algorithm_message: Any, metrics: Any) -> dict[str, Any]:
        experience = self.registry.record_experience(record_id, source, created_at, request, result, consent_status)
        if experience["status"] != "experience_recorded":
            return {"status": "learning_blocked", "experience": experience, "execution_authority": "none", "automatic_execution": False}
        evaluation = evaluate_candidate(metrics)
        if evaluation["status"] != "passed":
            return {"status": "learning_candidate_rejected", "experience": experience, "evaluation": evaluation, "execution_authority": "none", "automatic_execution": False}
        candidate = self.registry.propose_candidate(record_id, candidate_id, capability, algorithm_message)
        return {"status": "learning_candidate_ready" if candidate["status"] == "candidate_proposed" else "learning_blocked", "experience": experience, "evaluation": evaluation, "candidate": candidate, "promotion_requires_human": True, "execution_authority": "none", "automatic_execution": False}
