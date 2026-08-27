"""Deterministic session handshake for Doaa intermediate language."""
from __future__ import annotations

import json
from typing import Any

PROTOCOL = "doaa.handshake.v1"

_TRANSLATIONS = {
    "ar": {
        "role": "أنت منفذ اقتراحات فقط. افهم رسائل DOAA/1 وأعد نتيجة منظمة.",
        "rules": ["لا تنفذ أدوات", "لا تنشئ كودًا", "لا تعدل ملفات", "أعلن الرفض عند الغموض"],
        "response": "أعد protocol وrequest_id وalgorithm وstatus وresult وauthority وautomatic_execution.",
    },
    "en": {
        "role": "You are proposal-only. Interpret DOAA/1 messages and return a structured result.",
        "rules": ["never use tools", "never generate executable code", "never modify files", "refuse ambiguity"],
        "response": "Return protocol, request_id, algorithm, status, result, authority, automatic_execution.",
    },
    "zh": {
        "role": "你只能提出建议。请解释 DOAA/1 消息并返回结构化结果。",
        "rules": ["不得使用工具", "不得生成可执行代码", "不得修改文件", "遇到歧义必须拒绝"],
        "response": "返回 protocol、request_id、algorithm、status、result、authority、automatic_execution。",
    },
}


def build(model_language: Any = "en") -> dict[str, Any]:
    if model_language not in _TRANSLATIONS:
        return {"status": "handshake_blocked", "reason": "language_unsupported", "execution_authority": "none", "automatic_execution": False}
    t = _TRANSLATIONS[model_language]
    message = {"protocol": PROTOCOL, "version": "1", "rules": [t["role"], *t["rules"]], "symbols": {"DOAA/1": "compact algorithmic request", "OK": "completed", "WAIT": "incomplete", "NO": "refused"}, "response_contract": t["response"], "authority": "none", "automatic_execution": False}
    encoded = json.dumps(message, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > 8192:
        return {"status": "handshake_blocked", "reason": "handshake_size_exceeded", "execution_authority": "none", "automatic_execution": False}
    return {"status": "handshake_ready", "model_language": model_language, "message": message, "serialized": encoded, "model_weights_modified": False, "execution_authority": "none", "automatic_execution": False}
