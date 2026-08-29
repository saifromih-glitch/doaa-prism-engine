from __future__ import annotations
from typing import Any

UNCERTAINTY={'none','source_incomplete','not_found'}


def parse_compact(text: str, expected_ids: list[str]) -> dict[str, Any]:
    records=[]; rejected=[]; seen=set()
    for line_no, raw in enumerate(text.splitlines(),1):
        line=raw.strip()
        if not line: continue
        parts=line.split('|')
        if len(parts)!=5:
            rejected.append({'line':line_no,'reason':'field_count','raw':line}); continue
        qid,answer,quote,uncertainty,units=parts
        if qid not in expected_ids:
            rejected.append({'line':line_no,'reason':'unknown_question_id','raw':line}); continue
        if qid in seen:
            rejected.append({'line':line_no,'reason':'duplicate_question_id','raw':line}); continue
        if not answer.strip() or not quote.strip() or uncertainty not in UNCERTAINTY:
            rejected.append({'line':line_no,'reason':'invalid_required_value','raw':line}); continue
        seen.add(qid)
        records.append({'question_id':qid,'answer':answer,'evidence_quote':quote,'uncertainty':uncertainty,'answer_units':units})
    missing=[x for x in expected_ids if x not in seen]
    return {'records':records,'rejected':rejected,'missing_question_ids':missing,'status':'accepted' if not rejected and not missing else 'partial_or_rejected','execution_authority':'none','automatic_execution':False}
