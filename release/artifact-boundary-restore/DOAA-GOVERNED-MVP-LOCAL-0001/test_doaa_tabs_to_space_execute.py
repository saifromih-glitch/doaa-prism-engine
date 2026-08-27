import hashlib,json,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import doaa_tabs_to_space_execute as m
def c(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
with tempfile.TemporaryDirectory() as t:
 r=Path(t); i=r/'i.csv'; o=r/'o.csv'; i.write_text('name,phone\nA\tB,010\t20\n',encoding='utf-8',newline='')
 p={'kind':'proposal','operation':'tabs_to_ascii_space','column':'name','arguments':{},'execution_authority':'none'}
 h={'status':'accepted_by_human','execution_authority':'none','proposal_sha256':hashlib.sha256(c(p).encode()).hexdigest(),'audit_record_sha256':'a'*64}
 x=m.execute({'input_path':str(i),'output_path':str(o),'allowed_root':str(r),'proposal':p,'human_review':h})
 assert x['status']=='tabs_to_space_executed_safe_file' and o.read_text(encoding='utf-8')=='name,phone\nA B,010\t20\n'
 print(json.dumps({'tests':1,'status':'passed','only_target_column_changed':True,'automatic_execution':False},ensure_ascii=False))
