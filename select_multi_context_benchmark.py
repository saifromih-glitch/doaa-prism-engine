import json
from pathlib import Path

selection = json.loads(Path('benchmark-data/arabicaqa/recurrent-context-selection.json').read_text(encoding='utf-8'))
# Use real groups 2-6, capped to three questions per context for a focused multi-context run.
chosen = []
for group in selection['top_groups'][1:6]:
    for case in group['cases'][:3]:
        chosen.append({'case_id': case['case_id'], 'question': case['question'], 'reference_answer': case['reference_answer'], 'context': group['context']})
result = {'dataset': selection['dataset'], 'source_selection': 'top_groups[1:6], first three cases per group', 'case_count': len(chosen), 'context_count': len({item['context'] for item in chosen}), 'cases': chosen}
Path('benchmark-data/arabicaqa/multi-context-selection.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'case_count': result['case_count'], 'context_count': result['context_count'], 'status': 'selected_real_cases'}, ensure_ascii=False))
