from __future__ import annotations
import json, os, time
from collections import defaultdict
from pathlib import Path
from openai import OpenAI
from doaa_answer_shape import build_request, validate_response, parse_json
from doaa_evidence_snippets import select_snippet
from doaa_context_extractor import extract_supported_answer

DATA = Path('benchmark-data/arabicaqa/multi-context-selection.json')
OUT = Path('benchmark-data/arabicaqa/manus-multi-context-verified-run.json')
MODEL = os.getenv('DOAA_MODEL','gpt-5-mini')
if os.getenv('DOAA_RUN_LIVE') != '1': raise SystemExit('live_run_requires_DOAA_RUN_LIVE_1')
data=json.loads(DATA.read_text(encoding='utf-8'))
client=OpenAI()

def call(messages, schema=None):
    start=time.perf_counter(); kwargs={'model':MODEL,'messages':messages,'max_completion_tokens':512}
    if schema: kwargs['response_format']=schema
    r=client.chat.completions.create(**kwargs); u=r.usage
    return {'content':r.choices[0].message.content or '','prompt_tokens':u.prompt_tokens,'completion_tokens':u.completion_tokens,'total_tokens':u.total_tokens,'latency_ms':round((time.perf_counter()-start)*1000,3)}

def overlap(a,b):
    x=set(a.split()); y=set(b.split()); return round(len(x&y)/len(y),6) if y else 0.0
item={'type':'object','properties':{'question_id':{'type':'string'},'answer':{'type':'string'},'evidence_quote':{'type':'string'},'uncertainty':{'type':'string','enum':['none','source_incomplete','not_found']},'answer_units':{'type':'string'}},'required':['question_id','answer','evidence_quote','uncertainty','answer_units'],'additionalProperties':False}
schema={'type':'json_schema','json_schema':{'name':'doaa_multi_verified','strict':True,'schema':{'type':'object','properties':{'answers':{'type':'array','items':item}},'required':['answers'],'additionalProperties':False}}}

groups=defaultdict(list)
for row in data['cases']: groups[row['context']].append(row)
base=[]
for row in data['cases']:
    prompt=f"السؤال: {row['question']}\n\nالسياق:\n{row['context']}"
    r=call([{'role':'system','content':'أجب من السياق فقط بإجابة عربية موجزة دون شرح.'},{'role':'user','content':prompt}])
    base.append({'case_id':row['case_id'],'reference_answer':row['reference_answer'],'answer':r['content'],'reference_overlap':overlap(r['content'],row['reference_answer']),'usage':r})

def messages(context, rows):
    qs=[]
    evidence=[]
    for r in rows:
        snippet=select_snippet(r['question'], context)
        bounded=snippet.get('snippet') if snippet.get('status') == 'snippet_ready' else context
        evidence.append({'question_id':r['case_id'],'evidence':bounded})
        qs.append({'question_id':r['case_id'],'question':r['question'],'question_type':build_request(r['case_id'],r['question'],context)['question_type']})
    return [{'role':'system','content':'doaa.alg.v2|أخرج JSON فقط. استخدم evidence الخاص بالسؤال فقط. evidence_quote اقتباس حرفي منه. لا تخمن ولا تخلط بين الأسئلة. إذا لم يكف الدليل فاستخدم uncertainty.'},{'role':'user','content':json.dumps({'evidence':evidence,'questions':qs},ensure_ascii=False,separators=(',',':'))}]

doaa=[]
for context, rows in groups.items():
    first=call(messages(context,rows),schema); payload=parse_json(first['content']); items={x.get('question_id'):x for x in payload.get('answers',[]) if isinstance(x,dict)}
    failed=[]
    for row in rows:
        req=build_request(row['case_id'],row['question'],context); item0=items.get(row['case_id'],{})
        verdict=validate_response(item0,req)
        route='evidence_snippet'
        if verdict['status']!='supported':
            local=extract_supported_answer(row['question'], context)
            if local.get('status') == 'candidate':
                local_item={'question_id':row['case_id'],'answer':local['answer'],'evidence_quote':local['evidence_quote'],'uncertainty':'none','answer_units':''}
                local_verdict=validate_response(local_item, req)
                if local_verdict['status']=='supported':
                    item0=local_item; verdict=local_verdict; route='local_extractive'
            if verdict['status']!='supported': failed.append(row)
        doaa.append({'case_id':row['case_id'],'reference_answer':row['reference_answer'],'answer':item0.get('answer',''),'reference_overlap':overlap(item0.get('answer',''),row['reference_answer']),'verification':verdict,'first_usage':first,'route':route})
    if failed:
        retry=call(messages(context,failed),schema); retry_payload=parse_json(retry['content'])
        for row in failed:
            item1=next((x for x in retry_payload.get('answers',[]) if x.get('question_id')==row['case_id']),{})
            verdict=validate_response(item1,build_request(row['case_id'],row['question'],context)); out=next(x for x in doaa if x['case_id']==row['case_id'])
            out.update({'retry_answer':item1.get('answer',''),'retry_reference_overlap':overlap(item1.get('answer',''),row['reference_answer']),'retry_verification':verdict,'retry_usage':retry})

bp=sum(x['usage']['prompt_tokens'] for x in base); bt=sum(x['usage']['total_tokens'] for x in base)
dp=sum(x['first_usage']['prompt_tokens']+x.get('retry_usage',{}).get('prompt_tokens',0) for x in doaa); dt=sum(x['first_usage']['total_tokens']+x.get('retry_usage',{}).get('total_tokens',0) for x in doaa)
final_overlap=[x.get('retry_reference_overlap',x['reference_overlap']) for x in doaa]
accepted=sum(1 for x in doaa if x.get('retry_verification',x['verification'])['status']=='supported')
report={'status':'live_multi_context_verified_complete','model':MODEL,'case_count':len(data['cases']),'context_count':len(groups),'baseline':{'calls':len(base),'prompt_tokens':bp,'total_tokens':bt,'mean_reference_overlap':round(sum(x['reference_overlap'] for x in base)/len(base),6)},'doaa':{'context_calls':len(groups),'retry_count':sum(1 for x in doaa if 'retry_usage' in x),'final_supported':accepted,'mean_reference_overlap_final':round(sum(final_overlap)/len(final_overlap),6),'prompt_tokens':dp,'total_tokens':dt},'prompt_token_saving_ratio':round((bp-dp)/bp,6),'total_token_saving_ratio':round((bt-dt)/bt,6),'safety_evaluated':False,'human_review_completed':False,'execution_authority':'none','automatic_execution':False,'rows':doaa}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('status','case_count','context_count','baseline','doaa','prompt_token_saving_ratio','total_token_saving_ratio','safety_evaluated')},ensure_ascii=False))
