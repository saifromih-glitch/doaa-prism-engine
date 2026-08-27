import hashlib,json,tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import doaa_source_registry as r
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'sources.jsonl'; excerpt='Evidence'; h=hashlib.sha256(excerpt.encode()).hexdigest()
 source={'source_url':'https://example.com/a','title':'A','excerpt':excerpt,'source_hash':h}
 x=r.record_source(source,p); assert x['status']=='source_recorded_append_only'
 assert len(p.read_text(encoding='utf-8').splitlines())==1
 source['source_hash']='0'*64; y=r.record_source(source,p); assert y['status']=='source_record_blocked'
print(json.dumps({'tests':2,'status':'passed','append_only':True,'hash_verified':True,'automatic_execution':False},ensure_ascii=False))
