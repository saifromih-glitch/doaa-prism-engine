"""Local Ollama bridge for doaa.alg.v1; transport remains injectable for tests."""
from __future__ import annotations

import json
from typing import Any, Callable

from doaa_algorithmic_mediator import mediate
from doaa_algorithmic_protocol import encode_request
from doaa_ollama_proposal_adapter import request_proposal


def prepare(request: Any, message_id: str, model_id: str, endpoint: str, timeout_seconds: float = 10) -> dict[str, Any]:
    checked = encode_request(request)
    if checked.get("status") != "algorithm_message_valid":
        return {"status": "ollama_bridge_blocked", "stage": "request", "detail": checked, "execution_authority": "none", "automatic_execution": False}
    return {"status": "ollama_algorithm_request_prepared", "payload": {"message_id": message_id, "model_id": model_id, "prompt": json.dumps(checked["message"], ensure_ascii=False, sort_keys=True, separators=(",", ":")), "execution_authority": "none", "endpoint": endpoint, "timeout_seconds": timeout_seconds}, "execution_authority": "none", "automatic_execution": False}


def call_and_mediate(request: Any, message_id: str, model_id: str, endpoint: str, transport: Callable[..., Any], timeout_seconds: float = 10) -> dict[str, Any]:
    prepared = prepare(request, message_id, model_id, endpoint, timeout_seconds)
    if prepared.get("status") != "ollama_algorithm_request_prepared":
        return prepared
    raw = request_proposal(prepared["payload"], transport=transport)
    if raw.get("status") != "ollama_raw_proposal_received":
        return {"status": "ollama_bridge_blocked", "stage": "transport", "detail": raw, "execution_authority": "none", "automatic_execution": False}
    try:
        model_result = json.loads(raw["raw_response"])
    except (TypeError, json.JSONDecodeError):
        return {"status": "ollama_bridge_blocked", "stage": "result", "reason": "structured_result_required", "execution_authority": "none", "automatic_execution": False}
    mediated = mediate(request, model_result)
    return {"status": "ollama_bridge_completed" if mediated.get("status") == "mediation_completed" else "ollama_bridge_blocked", "raw_model_result": model_result, "mediation": mediated, "model_result_trusted": False, "execution_authority": "none", "automatic_execution": False}
