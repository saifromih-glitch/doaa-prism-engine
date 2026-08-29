import json
from collections import defaultdict
from doaa_evidence_snippets import select_snippet

data=json.load(open('benchmark-data/arabicaqa/multi-context-selection.json',encoding='utf8'))
groups=defaultdict(list)
for row in data['cases']: groups[row['context']].append(row)
for i,(context,rows) in enumerate(groups.items(),1):
    print({'group':i,'context_chars':len(context),'questions':len(rows),'snippet_chars':[len(select_snippet(r['question'],context).get('snippet','')) for r in rows],'coverage':[select_snippet(r['question'],context).get('coverage',0) for r in rows]})
