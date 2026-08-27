"""Pure mediation boundary: validate request, validate raw model result, render text."""
from __future__ import annotations

from typing import Any

from doaa_algorithmic_protocol import encode_request, render_result, validate_result


def mediate(request: Any, raw_model_result: Any) -> dict[str, Any]:
    """Never calls a model; accepts only an already returned raw result."""
    encoded = encode_request(request)
    if encoded.get("status") != "algorithm_message_valid":
        return {"status": "mediation_blocked", "stage": "request", "detail": encoded, "execution_authority": "none", "automatic_execution": False}
    checked = validate_result(raw_model_result, encoded["message"])
    if checked.get("status") != "algorithm_result_valid":
        return {"status": "mediation_blocked", "stage": "result", "detail": checked, "execution_authority": "none", "automatic_execution": False}
    rendered = render_result(checked)
    return {"status": "mediation_completed", "request": encoded["message"], "validated_result": checked["result"], "rendered": rendered, "model_result_trusted": False, "execution_authority": "none", "automatic_execution": False}
