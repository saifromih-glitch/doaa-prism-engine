"""Governed packaging for a warm model session using Semantic Checkpoints."""
from __future__ import annotations

from typing import Any

from doaa_semantic_checkpoint import SemanticCheckpointStore

CONTRACT = "doaa.warm_checkpoint.v1"


class WarmCheckpointSession:
    def __init__(self, session_id: str, store: SemanticCheckpointStore | None = None) -> None:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id_required")
        self.session_id = session_id
        self.store = store or SemanticCheckpointStore()
        self.checkpoint_id: str | None = None
        self.source_registered = False
        self.closed = False
        self.request_count = 0

    def register_source(self, source_text: Any) -> dict[str, Any]:
        if self.closed:
            return self._blocked("session_closed")
        if self.source_registered:
            return self._blocked("source_already_registered")
        created = self.store.create(source_text)
        if created["status"] != "checkpoint_created":
            return self._blocked(created.get("reason", "checkpoint_create_failed"))
        self.checkpoint_id = created["checkpoint_id"]
        self.source_registered = True
        return {"status": "source_registered", "contract": CONTRACT, "session_id": self.session_id, "checkpoint_id": self.checkpoint_id, "source_sent_once": True, "execution_authority": "none", "automatic_execution": False}

    def prepare_query(self, question: Any, segment_ids: list[str] | None = None) -> dict[str, Any]:
        if self.closed:
            return self._blocked("session_closed")
        if not self.source_registered or self.checkpoint_id is None:
            return self._blocked("source_registration_required")
        compact = self.store.compact_query(self.checkpoint_id, question, segment_ids)
        if compact["status"] != "compact_reference_ready":
            return self._blocked(compact.get("reason", "compact_query_failed"))
        self.request_count += 1
        return {"status": "warm_query_ready", "contract": CONTRACT, "session_id": self.session_id, "payload": compact["payload"], "source_sent_once": False, "request_count": self.request_count, "fallback": "send_source_again_only_after_explicit_session_reset", "execution_authority": "none", "automatic_execution": False}

    def expand_for_verification(self, payload: Any) -> dict[str, Any]:
        if self.closed:
            return self._blocked("session_closed")
        return self.store.expand(payload)

    def close(self) -> dict[str, Any]:
        self.closed = True
        return {"status": "warm_session_closed", "contract": CONTRACT, "session_id": self.session_id, "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "warm_checkpoint_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
