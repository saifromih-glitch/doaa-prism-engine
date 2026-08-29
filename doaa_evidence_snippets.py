from __future__ import annotations
import re
from typing import Any
from doaa_context_extractor import _tokens


def select_snippet(question: str, context: str, max_sentences: int = 3) -> dict[str, Any]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!؟؛])\s+|\n+", context) if s.strip()]
    q = _tokens(question)
    ranked=[]
    for i,s in enumerate(sentences):
        st=_tokens(s)
        matched={term for term in q if any(term == x or (len(term)>=4 and len(x)>=4 and (term.startswith(x) or x.startswith(term))) for x in st)}
        score=len(matched)/max(1,len(q)) + (0.1 if re.search(r'\d',s) and q & {"نسبة","عدد","مساحة","ارتفاع","متوسط","دخل","العمر"} else 0)
        ranked.append((score,len(matched),-i,s,matched))
    ranked.sort(reverse=True)
    chosen=[]; covered=set()
    for _,_,_,sentence,matched in ranked:
        if not matched or sentence in chosen: continue
        if matched-covered or not chosen:
            chosen.append(sentence); covered |= matched
        if len(chosen)>=max_sentences or covered>=q: break
    if not chosen or not covered:
        return {"status":"fallback_or_review","reason":"no_bounded_evidence","execution_authority":"none"}
    return {"status":"snippet_ready","snippet":" ".join(chosen),"evidence_quotes":chosen,"matched_terms":sorted(covered),"coverage":round(len(covered)/max(1,len(q)),6),"execution_authority":"none","automatic_execution":False}
