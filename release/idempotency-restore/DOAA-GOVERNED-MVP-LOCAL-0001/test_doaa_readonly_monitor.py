import hashlib,json,tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import doaa_readonly_monitor as m
with tempfile.TemporaryDirectory() as t:
 r=Path(t); f=r/'a.txt'; f.write_text('ok',encoding='utf-8'); h=hashlib.sha256(f.read_bytes()).hexdigest(); man=r/'manifest.json'; man.write_text(json.dumps({'files':[{'path':'a.txt','sha256':h}]}),encoding='utf-8')
 x=m.monitor(r,man); assert x['status']=='monitor_ok' and x['repair_started'] is False
 f.write_text('changed',encoding='utf-8'); y=m.monitor(r,man); assert y['status']=='monitor_alert' and y['repair_started'] is False
print(json.dumps({'tests':2,'status':'passed','read_only':True,'self_repair':False},ensure_ascii=False))
