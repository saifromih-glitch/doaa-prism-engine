"""Transparent token-related metrics; no claim of model tokenizer equivalence."""
from __future__ import annotations

import json
import re
from typing import Any

TOKENISH = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def estimate_units(text: str) -> int:
    if not isinstance(text, str):
        raise TypeError("text_required")
    return len(TOKENISH.findall(text))


def measure(text: str, source: str) -> dict[str, Any]:
    if source not in {"natural_prompt", "algorithm_message"}:
        raise ValueError("source_invalid")
    return {"source": source, "characters": len(text), "utf8_bytes": len(text.encode("utf-8")), "estimated_token_units": estimate_units(text), "estimator": "unicode_word_punctuation_proxy"}


def compare(natural_prompt: str, algorithm_message: dict[str, Any]) -> dict[str, Any]:
    natural = measure(natural_prompt, "natural_prompt")
    encoded = json.dumps(algorithm_message, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    compressed = measure(encoded, "algorithm_message")
    baseline = natural["estimated_token_units"]
    compact = compressed["estimated_token_units"]
    saving = (baseline - compact) / baseline if baseline else 0.0
    return {"status": "metrics_computed", "natural": natural, "algorithmic": compressed, "estimated_saving_ratio": round(saving, 6), "is_model_usage": False}
