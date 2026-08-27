"""Build a protocol request only from a validated curated algorithm proposal."""
from __future__ import annotations

from typing import Any

from doaa_algorithmic_protocol import encode_request


def build(proposal: Any, text: Any, request_id: str, language: str = "ar") -> dict[str, Any]:
    if not isinstance(proposal, dict) or proposal.get("status") != "algorithmic_classification_proposal" or proposal.get("requires_validation") is not True:
        return {"status": "request_build_blocked", "reason": "validated_proposal_required", "execution_authority": "none", "automatic_execution": False}
    algorithm = proposal.get("algorithm")
    if not isinstance(text, str) or not text.strip():
        return {"status": "request_build_blocked", "reason": "text_required", "execution_authority": "none", "automatic_execution": False}
    request = {
        "protocol": "doaa.alg.v1", "request_id": request_id,
        "algorithm": algorithm, "parameters": {"language": language},
        "context": {"algorithm_refs": [algorithm["id"]], "user_constraints": []},
        "input": {"kind": "text", "value": text},
        "output_policy": {"format": "natural_language", "language": language},
        "authority": "none", "automatic_execution": False,
    }
    checked = encode_request(request)
    if checked.get("status") != "algorithm_message_valid":
        return {"status": "request_build_blocked", "reason": checked.get("reason", "request_invalid"), "execution_authority": "none", "automatic_execution": False}
    return {"status": "algorithm_request_built", "message": checked["message"], "source_proposal": "validated_curated_alias", "execution_authority": "none", "automatic_execution": False}
