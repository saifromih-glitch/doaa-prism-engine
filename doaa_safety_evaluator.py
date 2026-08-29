from __future__ import annotations
import re
from typing import Any

PATTERNS = {
    "prompt_injection": ("ignore previous", "تجاهل التعليمات السابقة", "انس التعليمات السابقة"),
    "unsupported_execution": ("نفذ الأمر", "شغل الأمر", "run command", "execute command", "sudo ", "rm -rf"),
    "secret_like": ("sk-", "ghp_", "api_key=", "password=")
}


def evaluate_answer(answer: Any, evidence: Any = "") -> dict[str, Any]:
    if not isinstance(answer, str) or not answer.strip():
        return _result("blocked", ["answer_empty"])
    if not isinstance(evidence, str):
        return _result("blocked", ["evidence_invalid"])
    findings = []
    lowered = answer.lower()
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in answer):
        findings.append("control_characters")
    for category, markers in PATTERNS.items():
        if any(marker.lower() in lowered for marker in markers):
            findings.append(category)
    if findings:
        return _result("review_required", findings)
    return _result("passed", [])


def _result(status: str, findings: list[str]) -> dict[str, Any]:
    return {"status": status, "findings": findings, "truth_verified": False, "execution_authority": "none", "automatic_execution": False}
