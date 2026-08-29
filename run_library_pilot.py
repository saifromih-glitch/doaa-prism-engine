from __future__ import annotations
import json, os, time
from pathlib import Path
from openai import OpenAI

ROOT=Path(__file__).parent
LIB=json.loads((ROOT/'library-pilot/software-security-seo.json').read_text(encoding='utf-8'))
MODEL=os.getenv('DOAA_MODEL','gpt-5-mini')
client=OpenAI()

def call(messages):
    t=time.perf_counter()
    r=client.chat.completions.create(model=MODEL,messages=messages,max_completion_tokens=700)
    u=r.usage
    return {'text':r.choices[0].message.content or '', 'prompt_tokens':u.prompt_tokens, 'completion_tokens':u.completion_tokens, 'total_tokens':u.total_tokens, 'latency_ms':round((time.perf_counter()-t)*1000,2)}

task='''أريد اختبار إطلاق صفحة عربية جديدة لخدمة برمجية صغيرة خلال 72 ساعة. صمّم خطة عملية قصيرة تشمل: فرضية الطلب، تحسين الصفحة لمحركات البحث دون وعود بالترتيب، مؤشرات القياس، ومراجعة أمنية أولية قبل الإطلاق. ميّز بين الحقائق والافتراضات، ولا تخترع أرقاماً أو بيانات سوق.'''

baseline=call([{'role':'system','content':'أجب بالعربية بدقة، وميّز بين الحقائق والافتراضات، ولا تخترع بيانات.'},{'role':'user','content':task}])
compact_entries=[{k:e[k] for k in ('id','domain','claim','source_url','source_status','allowed_use','forbidden_inference')} for e in LIB['entries']]
library_prompt=task+'\n\nمكتبة Doaa الموثقة (استخدمها كقيود ومراجع، ولا توسّع دلالتها):\n'+json.dumps(compact_entries,ensure_ascii=False,separators=(',',':'))+'\n\nأخرج خطة قابلة للتنفيذ مع ربط كل قاعدة بمعرف المصدر، واذكر ما يحتاج تحققاً بشرياً.'
with_library=call([{'role':'system','content':'doaa.library.v1|استخدم الادعاءات المرفقة فقط كمعرفة مصدرية. لا تحول الإرشادات إلى ضمانات. أجب بالعربية.'},{'role':'user','content':library_prompt}])

result={'status':'live_library_pilot_complete','model':MODEL,'task':task,'library_id':LIB['library_id'],'library_entries':len(LIB['entries']),'baseline':baseline,'with_library':with_library,'prompt_token_delta':with_library['prompt_tokens']-baseline['prompt_tokens'],'total_token_delta':with_library['total_tokens']-baseline['total_tokens'],'prompt_saving_ratio':round((baseline['prompt_tokens']-with_library['prompt_tokens'])/max(1,baseline['prompt_tokens']),6),'total_saving_ratio':round((baseline['total_tokens']-with_library['total_tokens'])/max(1,baseline['total_tokens']),6),'human_quality_review':False,'execution_authority':'none','automatic_promotion':False}
(ROOT/'library-pilot/library-pilot-live-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','model','library_entries','baseline','with_library','prompt_token_delta','total_token_delta','prompt_saving_ratio','total_saving_ratio')},ensure_ascii=False))
