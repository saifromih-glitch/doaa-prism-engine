from __future__ import annotations
import json
from pathlib import Path
from doaa_efficiency_router import choose_route

INPUT = Path('benchmark-data/arabicaqa/multi-context-selection.json')
OUTPUT = Path('benchmark-data/arabicaqa/efficiency-router-local-run.json')

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    rows=[]
    for context_name, cases in data.items():
        if not isinstance(cases, list):
            continue
        for case in cases:
            question = case.get('question') or case.get('question_ar') or case.get('query') or ''
            context = case.get('context') or case.get('context_ar') or ''
            if not question or not context:
                continue
            decision = choose_route(question, context, question_count=len(cases))
            rows.append({'context_name':context_name,'case_id':case.get('id'),'question':question,'decision':decision})
    routes={}
    total_base=total_doaa=0
    for row in rows:
        d=row['decision']; routes[d['route']]=routes.get(d['route'],0)+1
        total_base += d['estimated_baseline_tokens']; total_doaa += d['estimated_doaa_tokens']
    summary={
        'cases':len(rows),
        'routes':routes,
        'estimated_baseline_tokens':total_base,
        'estimated_router_tokens':total_doaa,
        'estimated_saving_ratio':round(1-total_doaa/max(1,total_base),6),
        'measurement_type':'local_estimate_only',
        'model_usage_tokens':None,
        'human_quality_review':False,
        'execution_authority':'none'
    }
    OUTPUT.write_text(json.dumps({'summary':summary,'rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
