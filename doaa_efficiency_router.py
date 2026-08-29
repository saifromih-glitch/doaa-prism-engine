from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from doaa_evidence_snippets import select_snippet
from doaa_route_cache import RouteCache

@dataclass
class RouteDecision:
    route: str
    reason: str
    estimated_baseline_tokens: int
    estimated_doaa_tokens: int
    estimated_saving_ratio: float
    safe: bool = True


def estimate_tokens(text: str) -> int:
    # محافظ تقريبي للمقارنة الداخلية فقط، وليس بديلاً عن usage API الحقيقي.
    return max(1, len(text.strip()) // 4)


def choose_route(question: str, context: str, question_count: int = 1, cache: RouteCache | None = None) -> dict[str, Any]:
    if cache and cache.get(context, question):
        return RouteDecision("local_exact", "cache_hit_exact_key", 0, 0, 1.0).__dict__
    snippet = select_snippet(question, context)
    if snippet["status"] == "snippet_ready" and snippet["coverage"] >= 0.5:
        base = estimate_tokens(context) + estimate_tokens(question)
        snip = estimate_tokens(snippet["snippet"]) + estimate_tokens(question) + 12
        # checkpoint لا يُختار إلا إذا كان السياق مشتركاً بما يكفي لتعويض overhead البروتوكول.
        checkpoint = estimate_tokens(context) + question_count * estimate_tokens(question) + 24
        snippet_batch = snip * question_count
        if question_count >= 3 and checkpoint < min(base * question_count * 0.70, snippet_batch * 0.85):
            route, predicted = "warm_checkpoint", checkpoint
            reason = "shared_context_amortizes_protocol_overhead"
        else:
            route, predicted = "evidence_snippet", snippet_batch
            reason = "bounded_evidence_batch_is_cheaper_than_full_checkpoint"
        saving = 1 - (predicted / max(1, base * question_count))
        return RouteDecision(route, reason, base * question_count, predicted, round(saving, 6)).__dict__
    return RouteDecision("baseline_or_review", "insufficient_local_evidence", estimate_tokens(context)+estimate_tokens(question), estimate_tokens(context)+estimate_tokens(question), 0.0, False).__dict__
