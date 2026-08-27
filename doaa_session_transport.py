"""Local stateful transport for Doaa handshake and algorithm messages.

This module only prepares payloads. It never calls a model, network, tool, or
executor. A provider adapter may consume the returned payload explicitly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from doaa_session_protocol import next_message, start


def _estimate_tokens(value: Any) -> int:
    """Conservative provider-independent proxy; real provider usage wins."""
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return max(1, (len(encoded.encode("utf-8")) + 3) // 4)


@dataclass
class LocalSessionTransport:
    session_id: str
    model_language: str = "en"
    _session: dict[str, Any] = field(init=False, repr=False)
    _closed: bool = field(default=False, init=False)
    request_count: int = field(default=0, init=False)
    handshake_count: int = field(default=0, init=False)
    prompt_proxy_tokens: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._session = start(self.session_id, self.model_language)

    @property
    def ready(self) -> bool:
        return self._session.get("status") == "session_ready" and not self._closed

    @property
    def session_state(self) -> dict[str, Any]:
        return dict(self._session)

    def prepare(self, algorithm_message: Any) -> dict[str, Any]:
        if self._closed:
            return self._blocked("session_closed")
        if not self.ready:
            return self._blocked(self._session.get("reason", "session_not_ready"))
        envelope = next_message(self._session, algorithm_message)
        if envelope.get("status") != "session_message_ready":
            return envelope
        handshake = envelope.get("handshake")
        self._session = dict(self._session)
        self._session["handshake_sent"] = True
        self.request_count += 1
        if handshake is not None:
            self.handshake_count += 1
        payload = {"session_id": self.session_id, "handshake": handshake, "message": algorithm_message}
        self.prompt_proxy_tokens += _estimate_tokens(payload)
        return {"status": "transport_payload_ready", "payload": payload, "handshake_sent": handshake is not None, "request_count": self.request_count, "execution_authority": "none", "automatic_execution": False}

    def close(self) -> dict[str, Any]:
        self._closed = True
        self._session = dict(self._session)
        self._session["status"] = "session_closed"
        return {"status": "session_closed", "session_id": self.session_id, "execution_authority": "none", "automatic_execution": False}

    def metrics(self) -> dict[str, Any]:
        return {"session_id": self.session_id, "requests": self.request_count, "handshakes": self.handshake_count, "prompt_proxy_tokens": self.prompt_proxy_tokens, "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "transport_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False}
