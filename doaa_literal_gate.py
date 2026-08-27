"""Deterministic, fail-closed literal-compliance gate for Doaa results.

This gate never asks a model to judge itself and never executes or modifies data.
It checks only explicit, machine-testable constraints supplied by the request.
"""
from __future__ import annotations

import re
from typing import Any

_NUM = re.compile(r"(?<![\w])\d(?:[\d,/:.-]*\d)?(?![\w])")
_SENTENCE = re.compile(r"[.!؟。！？]+")


def _blocked(reason: str, details: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": "literal_compliance_blocked",
        "passed": False,
        "reason": reason,
        "details": details or [],
        "execution_authority": "none",
        "automatic_execution": False,
    }


def _numbers(text: str) -> set[str]:
    return {x.replace(",", "") for x in _NUM.findall(text)}


def _sentences(text: str) -> int:
    return len([x for x in _SENTENCE.findall(text) if x])


def check(request: Any, result_text: Any) -> dict[str, Any]:
    """Check an explicitly declared literal policy; unknown constraints fail closed."""
    if not isinstance(request, dict) or not isinstance(result_text, str):
        return _blocked("input_invalid")
    context = request.get("context")
    policy = context.get("literal_policy") if isinstance(context, dict) else None
    if not isinstance(policy, dict) or policy.get("mode") != "literal_only":
        return {"status": "literal_compliance_not_requested", "passed": True, "execution_authority": "none", "automatic_execution": False}
    source = request.get("input", {}).get("value") if isinstance(request.get("input"), dict) else None
    if not isinstance(source, str):
        return _blocked("source_required")
    issues: list[str] = []
    source_numbers = _numbers(source)
    result_numbers = _numbers(result_text)
    if not result_numbers.issubset(source_numbers):
        issues.append("new_numeric_literal")
    required = policy.get("required_literals", [])
    if not isinstance(required, list) or not all(isinstance(x, str) and x for x in required):
        return _blocked("required_literals_policy_invalid")
    missing = [x for x in required if x not in result_text]
    if missing:
        issues.append("required_literal_missing:" + "|".join(missing[:8]))
    forbidden = policy.get("forbidden_patterns", [])
    if not isinstance(forbidden, list) or not all(isinstance(x, str) and x for x in forbidden):
        return _blocked("forbidden_patterns_policy_invalid")
    hits = [x for x in forbidden if x in result_text]
    if hits:
        issues.append("forbidden_pattern_present:" + "|".join(hits[:8]))
    exact_sentences = policy.get("exact_sentence_count")
    if exact_sentences is not None:
        if not isinstance(exact_sentences, int) or exact_sentences < 1 or exact_sentences > 100:
            return _blocked("sentence_policy_invalid")
        count = _sentences(result_text)
        if count != exact_sentences:
            issues.append(f"sentence_count:{count}!={exact_sentences}")
    max_chars = policy.get("max_chars")
    if max_chars is not None:
        if not isinstance(max_chars, int) or max_chars < 1 or max_chars > 65536:
            return _blocked("max_chars_policy_invalid")
        if len(result_text) > max_chars:
            issues.append("max_chars_exceeded")
    if issues:
        return _blocked("explicit_literal_constraint_failed", issues)
    return {
        "status": "literal_compliance_passed",
        "passed": True,
        "checks": ["numbers_subset_of_source", "required_literals", "forbidden_patterns", "shape_limits"],
        "execution_authority": "none",
        "automatic_execution": False,
    }
