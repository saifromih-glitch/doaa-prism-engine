"""Compact reusable references; definitions are static and never learned automatically."""
from __future__ import annotations

import json
import re
from typing import Any

REFERENCES = {
    "R1": {"algorithm_id": "answer.summarize.v1", "definition": "summarize input faithfully in requested language; preserve facts; no tools"},
    "R2": {"algorithm_id": "answer.compose.v1", "definition": "compose a direct answer in requested language; no tools"},
    "R3": {"algorithm_id": "task.plan.v1", "definition": "produce an ordered plan; do not execute steps"},
}


def reference_definition(ref: Any) -> dict[str, Any] | None:
    if not isinstance(ref, str) or ref not in REFERENCES:
        return None
    return dict(REFERENCES[ref])


def encode(ref: Any, content: Any, language: str = "ar", limit: int = 3) -> dict[str, Any]:
    definition = reference_definition(ref)
    if definition is None:
        return {"status": "compact_request_blocked", "reason": "reference_unknown", "authority": "none", "automatic_execution": False}
    if not isinstance(content, str) or not content.strip() or not isinstance(language, str) or language not in {"ar", "en", "zh"}:
        return {"status": "compact_request_blocked", "reason": "content_or_language_invalid", "authority": "none", "automatic_execution": False}
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 20:
        return {"status": "compact_request_blocked", "reason": "limit_invalid", "authority": "none", "automatic_execution": False}
    message = {"p": "doaa.alg.v1", "r": ref, "l": language, "n": limit, "x": content, "e": False}
    serialized = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
    if len(serialized.encode("utf-8")) > 8192:
        return {"status": "compact_request_blocked", "reason": "request_too_large", "authority": "none", "automatic_execution": False}
    return {"status": "compact_request_ready", "reference": ref, "algorithm_id": definition["algorithm_id"], "message": message, "serialized": serialized, "authority": "none", "automatic_execution": False}
