"""Lossless local checkpoints for warm Doaa sessions."""
from __future__ import annotations

import hashlib
import re
from typing import Any

CONTRACT = "doaa.semantic_checkpoint.v1"
CHECKPOINT_RE = re.compile(r"^[a-f0-9]{64}$")
CRITICAL_RE = re.compile(r"\d+(?:[.,/]\d+)*|[\u064B-\u065F]|لا|ليس|لم|لن|غير|بدون|إلا|سوى", re.UNICODE)


class SemanticCheckpointStore:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def create(self, source_text: Any) -> dict[str, Any]:
        if not isinstance(source_text, str) or not source_text.strip():
            return self._blocked("source_text_required")
        normalized = source_text.replace("\r\n", "\n")
        checkpoint_id = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        segments = [segment for segment in re.split(r"(?<=[.!؟؛])\s+|\n+", normalized) if segment]
        record = {"checkpoint_id": checkpoint_id, "contract": CONTRACT, "source_sha256": checkpoint_id, "source_text": normalized, "segments": [{"segment_id": f"{index:04d}", "text": segment, "critical_tokens": CRITICAL_RE.findall(segment)} for index, segment in enumerate(segments)], "segment_count": len(segments), "execution_authority": "none", "automatic_execution": False}
        self._records[checkpoint_id] = record
        return {"status": "checkpoint_created", "checkpoint_id": checkpoint_id, "segment_count": len(segments), "critical_token_count": sum(len(segment["critical_tokens"]) for segment in record["segments"]), "execution_authority": "none", "automatic_execution": False}

    def compact_query(self, checkpoint_id: Any, question: Any, segment_ids: list[str] | None = None) -> dict[str, Any]:
        if not isinstance(checkpoint_id, str) or not CHECKPOINT_RE.fullmatch(checkpoint_id) or checkpoint_id not in self._records:
            return self._blocked("checkpoint_unknown")
        if not isinstance(question, str) or not question.strip():
            return self._blocked("question_required")
        record = self._records[checkpoint_id]
        allowed = {segment["segment_id"] for segment in record["segments"]}
        selected = segment_ids if segment_ids is not None else sorted(allowed)
        if not isinstance(selected, list) or not selected or any(item not in allowed for item in selected):
            return self._blocked("segment_reference_invalid")
        return {"status": "compact_reference_ready", "contract": CONTRACT, "payload": {"v": 1, "ck": checkpoint_id, "q": question, "s": selected}, "source_sha256": record["source_sha256"], "cold_session_requires_source": True, "execution_authority": "none", "automatic_execution": False}

    def expand(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict) or payload.get("v") != 1 or not isinstance(payload.get("ck"), str):
            return self._blocked("compact_reference_invalid")
        record = self._records.get(payload["ck"])
        if record is None:
            return self._blocked("checkpoint_unknown")
        selected = payload.get("s")
        if not isinstance(selected, list) or any(item not in {segment["segment_id"] for segment in record["segments"]} for item in selected):
            return self._blocked("segment_reference_invalid")
        selected_segments = [segment for segment in record["segments"] if segment["segment_id"] in selected]
        selected_ids = [segment["segment_id"] for segment in selected_segments]
        all_ids = [segment["segment_id"] for segment in record["segments"]]
        text = record["source_text"] if selected_ids == all_ids else "\n".join(segment["text"] for segment in selected_segments)
        return {"status": "checkpoint_expanded", "contract": CONTRACT, "checkpoint_id": payload["ck"], "question": payload.get("q"), "text": text, "source_sha256": record["source_sha256"], "lossless": selected_ids == all_ids, "execution_authority": "none", "automatic_execution": False}

    def get(self, checkpoint_id: Any) -> dict[str, Any]:
        record = self._records.get(checkpoint_id)
        if record is None:
            return self._blocked("checkpoint_unknown")
        return {"status": "checkpoint_ready", "checkpoint_id": checkpoint_id, "source_sha256": record["source_sha256"], "segment_count": record["segment_count"], "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "checkpoint_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
