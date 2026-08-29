import json
from pathlib import Path
from doaa_safety_evaluator import evaluate_answer
p=Path('benchmark-data/arabicaqa/manus-multi-context-verified-run.json')
r=json.loads(p.read_text(encoding='utf-8'))
rows=[]
for row in r['rows']:
    answer=row.get('retry_answer',row.get('answer',''))
    safety=evaluate_answer(answer)
    verification=row.get('retry_verification',row['verification'])
    rows.append({'case_id':row['case_id'],'verification':verification['status'],'safety':safety['status']})
summary={'case_count':len(rows),'supported_count':sum(x['verification']=='supported' for x in rows),'safety_passed_count':sum(x['safety']=='passed' for x in rows),'review_count':sum(x['verification']!='supported' or x['safety']!='passed' for x in rows),'prompt_token_saving_ratio':r['prompt_token_saving_ratio'],'total_token_saving_ratio':r['total_token_saving_ratio'],'human_review_completed':False,'truth_verified':False,'rows':rows}
Path('benchmark-data/arabicaqa/manus-multi-context-safety-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:summary[k] for k in ('case_count','supported_count','safety_passed_count','review_count','prompt_token_saving_ratio','total_token_saving_ratio','human_review_completed')},ensure_ascii=False))
