"""Conservative natural-language classifier; output is proposal-only."""
from __future__ import annotations

import re
from typing import Any

ALIASES = {
    "لخص النص": "answer.summarize.v1",
    "لخص النص بالعربية": "answer.summarize.v1",
    "summarize text": "answer.summarize.v1",
    "اكتب إجابة": "answer.compose.v1",
    "اكتب اجابة": "answer.compose.v1",
    "compose answer": "answer.compose.v1",
    "خطط للمهمة": "task.plan.v1",
    "خطط لمهمة": "task.plan.v1",
    "plan task": "task.plan.v1",
}


def _normalize(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    return re.sub(r"\s+", " ", text.strip())


def propose(text: Any, language: str = "ar") -> dict[str, Any]:
    normalized = _normalize(text)
    if normalized is None or not normalized:
        return {"status": "natural_proposal_blocked", "reason": "text_required", "execution_authority": "none", "automatic_execution": False}
    if not isinstance(language, str) or language not in {"ar", "en"}:
        return {"status": "natural_proposal_blocked", "reason": "language_unsupported", "execution_authority": "none", "automatic_execution": False}
    algorithm_id = ALIASES.get(normalized.casefold())
    if not algorithm_id:
        return {"status": "governed_capability_request", "reason": "natural_intent_not_exactly_registered", "input_preserved": True, "execution_authority": "none", "automatic_execution": False}
    return {"status": "algorithmic_classification_proposal", "algorithm": {"id": algorithm_id, "version": "1"}, "source": "exact_curated_alias", "requires_validation": True, "requires_review": True, "execution_authority": "none", "automatic_execution": False}
