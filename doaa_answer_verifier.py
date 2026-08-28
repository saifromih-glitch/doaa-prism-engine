"""Conservative, extractive answer verification for Doaa."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

CONTRACT = "doaa.answer_verification.v1"
WORD_RE = re.compile(r"[\w\u0600-\u06ff]+", re.UNICODE)
STOPWORDS = {"من", "ما", "هو", "هي", "في", "على", "إلى", "عن", "أن", "إن", "و", "أو", "ل", "ب", "ك", "الذي", "التي", "هذا", "هذه", "ذلك", "تلك", "عام", "فيه", "بها", "له", "لها"}


def verify_answer(question: Any, context: Any, answer: Any) -> dict[str, Any]:
    if not all(isinstance(value, str) for value in (question, context, answer)):
        return _blocked("input_text_required")
    if not question.strip() or not context.strip():
        return _blocked("question_or_context_empty")
    if not answer.strip():
        return _result("empty", "answer_empty", answer, [], 0.0)
    context_norm = _normalize(context)
    answer_norm = _normalize(answer)
    if answer_norm and answer_norm in context_norm:
        return _result("supported", "exact_context_span", answer, [], 1.0)
    context_terms = set(_terms(context))
    answer_terms = [term for term in _terms(answer) if term not in STOPWORDS]
    if not answer_terms:
        return _result("unsupported", "no_verifiable_terms", answer, [], 0.0)
    unsupported = sorted({term for term in answer_terms if term not in context_terms})
    numeric_or_symbolic = sorted({term for term in unsupported if any(char.isdigit() for char in term)})
    coverage = round((len(answer_terms) - len(unsupported)) / len(answer_terms), 6)
    if numeric_or_symbolic:
        return _result("unsupported", "unseen_numeric_term", answer, unsupported, coverage)
    if unsupported or coverage < 1.0:
        return _result("unsupported", "unsupported_answer_terms", answer, unsupported, coverage)
    return _result("supported", "all_significant_terms_in_context", answer, [], coverage)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _terms(text: str) -> list[str]:
    return [_normalize(term) for term in WORD_RE.findall(text)]


def _result(verdict: str, reason: str, answer: str, unsupported: list[str], coverage: float) -> dict[str, Any]:
    return {"status": verdict, "contract": CONTRACT, "reason": reason, "answer": answer, "unsupported_terms": unsupported, "term_coverage": coverage, "semantic_truth_claim": False, "fallback_action": "accept_for_review" if verdict == "supported" else "explicit_retry_or_human_review", "automatic_retry": False, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "blocked", "contract": CONTRACT, "reason": reason, "semantic_truth_claim": False, "automatic_retry": False, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}
