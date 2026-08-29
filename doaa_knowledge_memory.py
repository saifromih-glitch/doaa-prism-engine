from __future__ import annotations
import re
from collections import defaultdict
from typing import Any

ARABIC_DIACRITICS = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')

def normalize_arabic(text: str) -> str:
    text = ARABIC_DIACRITICS.sub('', text.lower())
    text = text.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي').replace('ـ','')
    return ' '.join(text.split())

def terms(text: str) -> set[str]:
    return {x for x in re.findall(r'[\wء-ي]+', normalize_arabic(text)) if len(x) >= 3}

class KnowledgeMemory:
    def __init__(self, entries: list[dict[str, Any]]):
        self.entries = entries
        self.index: dict[str, set[int]] = defaultdict(set)
        for i, entry in enumerate(entries):
            searchable = ' '.join(str(entry.get(k,'')) for k in ('domain','claim','allowed_use'))
            for term in terms(searchable): self.index[term].add(i)

    def retrieve(self, query: str, domain: str | None = None, top_k: int = 3) -> dict[str, Any]:
        q = terms(query)
        candidates = set()
        for term in q: candidates |= self.index.get(term, set())
        ranked=[]
        for i in candidates:
            e=self.entries[i]
            if domain and e.get('domain') != domain: continue
            et=terms(' '.join(str(e.get(k,'')) for k in ('domain','claim','allowed_use')))
            overlap=q & et
            score=len(overlap)/max(1,len(q))
            if e.get('domain') == domain: score += 0.20
            if e.get('source_status') in {'archived','stale'}: score -= 0.10
            ranked.append((score, len(overlap), e.get('id',''), e, overlap))
        ranked.sort(key=lambda x:(x[0],x[1],x[2]), reverse=True)
        selected=ranked[:max(0,top_k)]
        warnings=[]
        for _,_,_,e,_ in selected:
            if e.get('source_status') in {'archived','stale'} or e.get('freshness') != 'current':
                warnings.append({'id':e.get('id'),'status':e.get('source_status'),'freshness':e.get('freshness')})
        conflicts=[]
        for i in range(len(selected)):
            for j in range(i+1,len(selected)):
                a,b=selected[i][3],selected[j][3]
                if a.get('domain')==b.get('domain') and a.get('claim')==b.get('claim') and a.get('id')!=b.get('id'):
                    conflicts.append([a.get('id'),b.get('id')])
        claims=[{'id':e.get('id'),'claim':e.get('claim'),'source_url':e.get('source_url'),'source_title':e.get('source_title')} for _,_,_,e,_ in selected]
        payload='\n'.join(f"{c['id']}|{c['claim']}|source={c['source_url']}" for c in claims)
        return {'query':query,'selected_ids':[c['id'] for c in claims],'selected_claims':claims,'coverage':round(sum(len(x[4]) for x in selected)/max(1,len(q)),6),'source_warnings':warnings,'unresolved_conflicts':conflicts,'prompt_payload':payload,'execution_authority':'none','automatic_execution':False}
