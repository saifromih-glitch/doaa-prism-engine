"""Explicit model-adapter boundary for Doaa sessions.

The core prepares requests and validates returned envelopes. It never chooses
or invokes an adapter automatically. Integrators must call an adapter explicitly.
"""
from __future__ import annotations

from typing import Any, Protocol

from doaa_session_transport import LocalSessionTransport


class ModelAdapter(Protocol):
    """Provider-owned boundary; implementations may call a model explicitly."""

    def complete(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...


def prepare_request(transport: LocalSessionTransport, algorithm_message: dict[str, Any]) -> dict[str, Any]:
    """Prepare a model payload without invoking any adapter."""
    return transport.prepare(algorithm_message)


def validate_adapter_result(result: Any) -> dict[str, Any]:
    """Accept only a structurally governed model result; fail closed otherwise."""
    if not isinstance(result, dict):
        return _blocked("adapter_result_not_object")
    if result.get("protocol") != "doaa.alg.v1":
        return _blocked("adapter_protocol_invalid")
    if result.get("authority") != "none" or result.get("automatic_execution") is not False:
        return _blocked("adapter_authority_invalid")
    if result.get("status") not in {"OK", "WAIT", "NO"}:
        return _blocked("adapter_status_invalid")
    return {"status": "adapter_result_accepted", "result": dict(result), "execution_authority": "none", "automatic_execution": False}


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "adapter_result_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
