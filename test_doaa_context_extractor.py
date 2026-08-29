import json
import re
from pathlib import Path
from doaa_context_extractor import extract_supported_answer

cases = json.loads(Path('benchmark-data/arabicaqa/test-cases.json').read_text(encoding='utf-8'))['cases']
selection = json.loads(Path('benchmark-data/arabicaqa/recurrent-context-selection.json').read_text(encoding='utf-8'))
ids = {item['case_id'] for item in selection['top_groups'][0]['cases']}
selected = [case for case in cases if case['case_id'] in ids]

def norm(text):
    return re.sub(r'\s+', ' ', text.replace('،','').replace('.','').strip())

results=[]
for case in selected:
    request=json.loads(case['request'])
    result=extract_supported_answer(request['question'], request['context'])
    assert result['status'] in {'candidate', 'fallback_or_review'}
    if result['status'] == 'candidate':
        results.append((case['reference_answer'], result['answer']))
exact=sum(1 for ref,answer in results if norm(ref) in norm(answer) or norm(answer) in norm(ref))
print(json.dumps({'tests':len(selected),'status':'passed','candidate_count':len(results),'fallback_count':len(selected)-len(results),'reference_containment':exact,'reference_containment_rate':round(exact/max(1,len(results)),4),'execution_authority':'none'},ensure_ascii=False))
