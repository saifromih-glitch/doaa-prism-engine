from __future__ import annotations

import json
from typing import Any

CONTRACT = "doaa.answer_shape.v1"
ALLOWED_TYPES = {"numeric", "entity", "location", "date", "short_fact", "multi_fact"}


def classify_question(question: str) -> str:
    q = question.strip()
    if any(token in q for token in ("نسبة", "عدد", "كم ", "كم؟", "مساحة", "ارتفاع", "دخل")):
        return "numeric"
    if "أين" in q or "ولاية" in q or "مدينة" in q:
        return "location"
    if "متى" in q or "عام" in q or "سنة" in q:
        return "date"
    if "من هو" in q or "ما هو" in q or "ما هي" in q:
        return "short_fact"
    return "multi_fact"


def build_request(question_id: str, question: str, context: str) -> dict[str, Any]:
    question_type = classify_question(question)
    return {"contract": CONTRACT, "question_id": question_id, "question_type": question_type, "source_context": context, "instruction": "أجب من السياق فقط، ولا تضف معلومة غير موجودة. أعد JSON مطابقاً للعقد."}


def validate_response(payload: Any, request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return _reject("json_object_required")
    required = {"question_id", "answer", "evidence_quote", "uncertainty", "answer_units"}
    if set(payload) != required:
        return _reject("schema_keys_mismatch")
    if payload["question_id"] != request["question_id"]:
        return _reject("question_id_mismatch")
    if not isinstance(payload["answer"], str) or not payload["answer"].strip():
        return _reject("answer_empty")
    if not isinstance(payload["evidence_quote"], str) or not payload["evidence_quote"].strip():
        return _reject("evidence_quote_empty")
    if payload["evidence_quote"] not in request["source_context"]:
        return _reject("evidence_quote_not_in_source")
    if payload["uncertainty"] not in {"none", "source_incomplete", "not_found"}:
        return _reject("uncertainty_invalid")
    if payload["answer_units"] is not None and not isinstance(payload["answer_units"], str):
        return _reject("answer_units_invalid")
    if payload["uncertainty"] == "none" and not _answer_terms_supported(payload["answer"], request["source_context"]):
        return _reject("answer_terms_not_supported")
    return {"status": "supported", "contract": CONTRACT, "question_id": request["question_id"], "answer": payload["answer"], "evidence_quote": payload["evidence_quote"], "uncertainty": payload["uncertainty"], "answer_units": payload["answer_units"], "execution_authority": "none", "automatic_execution": False}


def _answer_terms_supported(answer: str, context: str) -> bool:
    words = [word.strip("،.؛:!?()[]{}\"'") for word in answer.split() if len(word.strip("،.؛:!?()[]{}\"'") ) >= 2]
    return all(word in context for word in words)


def _reject(reason: str) -> dict[str, Any]:
    return {"status": "fallback_or_review", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}


def parse_json(text: str) -> Any:
    return json.loads(text)
