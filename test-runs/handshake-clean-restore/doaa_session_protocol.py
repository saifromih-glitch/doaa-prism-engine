"""Session-scoped handshake state; in-memory and immutable from model output."""
from __future__ import annotations

import re
from typing import Any

from doaa_handshake import build

ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")


def start(session_id: Any, model_language: str = "en") -> dict[str, Any]:
    if not isinstance(session_id, str) or not ID_RE.fullmatch(session_id):
        return {"status": "session_blocked", "reason": "session_identity_invalid", "execution_authority": "none", "automatic_execution": False}
    handshake = build(model_language)
    if handshake.get("status") != "handshake_ready":
        return {"status": "session_blocked", "reason": handshake.get("reason", "handshake_invalid"), "execution_authority": "none", "automatic_execution": False}
    return {"status": "session_ready", "session_id": session_id, "model_language": model_language, "handshake": handshake["message"], "handshake_sent": False, "model_weights_modified": False, "execution_authority": "none", "automatic_execution": False}


def next_message(session: Any, algorithm_message: Any) -> dict[str, Any]:
    if not isinstance(session, dict) or session.get("status") != "session_ready" or session.get("execution_authority") != "none" or session.get("automatic_execution") is not False:
        return {"status": "session_message_blocked", "reason": "session_not_ready", "execution_authority": "none", "automatic_execution": False}
    if not isinstance(algorithm_message, dict) or algorithm_message.get("protocol") != "doaa.alg.v1":
        return {"status": "session_message_blocked", "reason": "algorithm_message_required", "execution_authority": "none", "automatic_execution": False}
    return {"status": "session_message_ready", "session_id": session["session_id"], "handshake": None if session.get("handshake_sent") else session["handshake"], "message": algorithm_message, "handshake_sent": True, "execution_authority": "none", "automatic_execution": False}
