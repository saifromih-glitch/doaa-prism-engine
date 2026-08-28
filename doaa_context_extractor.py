from __future__ import annotations
import re
from typing import Any

STOPWORDS = {"ما", "هو", "هي", "من", "في", "على", "عن", "كم", "التي", "الذي", "إلى", "عام", "سنة", "هل", "و", "أو", "بورتاج", "منطقة", "السكنية"}
NUMERIC_CUES = {"نسبة", "عدد", "مساحة", "ارتفاع", "دخل", "متوسط", "العمر", "الكثافة", "سكان", "أسر", "عائلات", "وحدات", "فئات"}

def _tokens(text: str) -> set[str]:
    tokens = {t for t in re.findall(r"[\wء-ي]+", text.lower()) if len(t) > 2 and t not in STOPWORDS}
    for token in list(tokens):
        if token.endswith("تها") and len(token) > 4:
            tokens.add(token[:-3] + "ة")
    return tokens

def _sentences(context: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!؟؛])\s+|\n+", context) if s.strip()]

def extract_supported_answer(question: str, context: str) -> dict[str, Any]:
    q_tokens = _tokens(question)
    if not q_tokens or not context.strip():
        return {"status": "fallback_or_review", "reason": "question_or_context_empty", "execution_authority": "none"}
    scored = []
    for index, sentence in enumerate(_sentences(context)):
        s_tokens = _tokens(sentence)
        overlap = {q for q in q_tokens if any(q == s or (len(q) >= 4 and len(s) >= 4 and (q.startswith(s) or s.startswith(q))) for s in s_tokens)}
        score = len(overlap) / max(1, len(q_tokens))
        cue_bonus = 0.15 if q_tokens & NUMERIC_CUES and re.search(r"\d", sentence) else 0.0
        scored.append((score + cue_bonus, len(overlap), -index, sentence, overlap))
    scored.sort(reverse=True)
    score, overlap_count, _, sentence, overlap = scored[0]
    if overlap_count == 0 or score < 0.20:
        return {"status": "fallback_or_review", "reason": "no_sufficient_question_evidence_match", "execution_authority": "none"}
    numbers = re.findall(r"\d[\d,.]*%?", sentence)
    question_is_numeric = bool(q_tokens & NUMERIC_CUES)
    answer = sentence
    if question_is_numeric and len(numbers) == 1:
        answer = numbers[0]
        unit_match = re.search(r"(?:%|نسمة|وحدة|أسرة|عائلة|عاماً|دولارًا)", sentence)
        if unit_match and not answer.endswith(unit_match.group(0)):
            answer += unit_match.group(0)
    return {"status": "candidate", "answer": answer, "evidence_quote": sentence, "matched_terms": sorted(overlap), "score": round(score, 6), "execution_authority": "none", "automatic_execution": False}
