from __future__ import annotations
import json, os, time
from pathlib import Path
from openai import OpenAI
from doaa_knowledge_memory import KnowledgeMemory
from doaa_compact_output import parse_compact
from doaa_route_cache import RouteCache

ROOT=Path(__file__).parent
LIB=json.loads((ROOT/'library-pilot/software-security-seo.json').read_text(encoding='utf-8'))
MODEL=os.getenv('DOAA_MODEL','gpt-5-mini'); client=OpenAI()
task='أعطني ثلاث خطوات لإطلاق صفحة عربية لخدمة برمجية خلال 72 ساعة، مع مؤشر قياس واحد وملاحظة أمان واحدة.'

def call(messages):
 t=time.perf_counter(); r=client.chat.completions.create(model=MODEL,messages=messages,max_completion_tokens=220)
 u=r.usage; return {'text':r.choices[0].message.content or '','prompt_tokens':u.prompt_tokens,'completion_tokens':u.completion_tokens,'total_tokens':u.total_tokens,'latency_ms':round((time.perf_counter()-t)*1000,2)}

baseline_calls=[call([{'role':'system','content':'أجب بالعربية في صيغة موجزة.'},{'role':'user','content':task}]) for _ in range(3)]
memory=KnowledgeMemory(LIB['entries']); retrieval=memory.retrieve(task,top_k=2)
ids=['q1']; prompt='doaa.compact.v1\nأجب في سطر واحد فقط وبخمسة حقول مفصولة بعلامة | بهذا الترتيب: q1|الإجابة|الاقتباس الحرفي|none|الوحدة. يجب أن تكون قيمة الحقل الرابع واحدة من none أو source_incomplete أو not_found فقط. لا تضع علامة | داخل الإجابة أو الاقتباس. لا تكتب أي نص آخر.\nالمهمة:'+task+'\nقواعد موثقة:'+retrieval['prompt_payload']
first=call([{'role':'system','content':'التزم بصيغة الإخراج المختصر حرفياً.'},{'role':'user','content':prompt}])
parsed=parse_compact(first['text'],ids)
cache=RouteCache(str(ROOT/'library-pilot/compact-cache.json'))
cache_key=cache.put('library:'+retrieval['prompt_payload'],task,parsed) if parsed['status']=='accepted' else None
reuse_hits=0
for _ in range(2):
 if cache.get('library:'+retrieval['prompt_payload'],task): reuse_hits+=1
result={'status':'live_compact_reuse_pilot_complete','model':MODEL,'task':task,'selected_entries':retrieval['selected_ids'],'retrieval_coverage':retrieval['coverage'],'compact_first_call':first,'parsed':parsed,'baseline_calls':baseline_calls,'cache_reuse_hits':reuse_hits,'baseline_prompt_tokens':sum(x['prompt_tokens'] for x in baseline_calls),'baseline_total_tokens':sum(x['total_tokens'] for x in baseline_calls),'doaa_model_prompt_tokens':first['prompt_tokens'],'doaa_model_total_tokens':first['total_tokens'],'doaa_amortized_prompt_tokens':first['prompt_tokens'],'doaa_amortized_total_tokens':first['total_tokens'],'prompt_saving_ratio':round((sum(x['prompt_tokens'] for x in baseline_calls)-first['prompt_tokens'])/max(1,sum(x['prompt_tokens'] for x in baseline_calls)),6),'total_saving_ratio':round((sum(x['total_tokens'] for x in baseline_calls)-first['total_tokens'])/max(1,sum(x['total_tokens'] for x in baseline_calls)),6),'human_quality_review':False,'execution_authority':'none'}
(ROOT/'library-pilot/compact-reuse-live-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','selected_entries','parsed','cache_reuse_hits','baseline_prompt_tokens','doaa_model_prompt_tokens','baseline_total_tokens','doaa_model_total_tokens','prompt_saving_ratio','total_saving_ratio')},ensure_ascii=False))
