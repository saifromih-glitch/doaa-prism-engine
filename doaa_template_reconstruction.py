"""Deterministic, local-only reconstruction from frozen Doaa templates."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.reconstruction.v1"
_MAX_VALUE_LENGTH = 512
_MAX_OUTPUT_LENGTH = 4096

_TEMPLATES: dict[str, dict[str, Any]] = {
    "marketing.campaign.v1": {
        "library": "marketing",
        "template": "campaign",
        "algorithm_id": "marketing.campaign.v1",
        "slot_order": ("goal", "audience", "channel", "language"),
    },
    "sales.pipeline.v1": {
        "library": "sales",
        "template": "pipeline",
        "algorithm_id": "sales.pipeline.v1",
        "slot_order": ("goal", "stage", "language"),
    },
    "software.task.v1": {
        "library": "software",
        "template": "task",
        "algorithm_id": "software.task.v1",
        "slot_order": ("goal", "language"),
    },
    "science.explain.v1": {
        "library": "science",
        "template": "explain",
        "algorithm_id": "science.explain.v1",
        "slot_order": ("topic", "level", "language"),
    },
}


class TemplateRegistry:
    """Frozen built-in template registry; no public mutation operation exists."""

    def get(self, template_id: Any) -> dict[str, Any] | None:
        if not isinstance(template_id, str):
            return None
        template = _TEMPLATES.get(template_id)
        return dict(template) if template else None

    def reconstruct(self, template_id: Any, slots: Any) -> dict[str, Any]:
        definition = self.get(template_id)
        if definition is None:
            return _proposal(template_id, "template_not_registered")
        if not isinstance(slots, dict):
            return _blocked("slots_must_be_object")
        expected = set(definition["slot_order"])
        if set(slots) - expected:
            return _blocked("unknown_slot")
        if set(slots) != expected:
            return _blocked("missing_required_slot", missing_slots=sorted(expected - set(slots)))
        normalized: dict[str, str] = {}
        for key in definition["slot_order"]:
            value = slots[key]
            if not isinstance(value, str) or not value or len(value) > _MAX_VALUE_LENGTH:
                return _blocked("slot_value_invalid", slot=key)
            normalized[key] = value
        request = {"capability": definition["algorithm_id"].removesuffix(".v1"), "slots": normalized}
        message = {
            "protocol": "doaa.alg.v1",
            "algorithm": {"id": definition["algorithm_id"], "version": "1"},
            "request": request,
            "authority": "none",
            "automatic_execution": False,
        }
        if len(str(message)) > _MAX_OUTPUT_LENGTH:
            return _blocked("reconstruction_output_too_large")
        return {
            "status": "reconstruction_ready",
            "contract": CONTRACT,
            "template_id": template_id,
            "library": definition["library"],
            "algorithm_id": definition["algorithm_id"],
            "slot_order": list(definition["slot_order"]),
            "request": request,
            "message": message,
            "source": "local_template_registry",
            "execution_authority": "none",
            "automatic_execution": False,
        }


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    return {"status": "reconstruction_blocked", "contract": CONTRACT, "reason": reason, **extra, "execution_authority": "none", "automatic_execution": False}


def _proposal(template_id: Any, reason: str) -> dict[str, Any]:
    return {"status": "governed_capability_request", "contract": CONTRACT, "requested_template": template_id, "reason": reason, "required_review": ["contract", "threat_model", "tests", "human_approval"], "execution_authority": "none", "automatic_execution": False}
