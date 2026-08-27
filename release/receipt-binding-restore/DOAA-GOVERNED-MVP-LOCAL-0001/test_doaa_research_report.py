import json,tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import doaa_research_report as r
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'sources.jsonl'; p.write_text(json.dumps({'source_url':'https://example.com','title':'T','excerpt':'E','source_hash':'h'})+'\n',encoding='utf-8')
 x=r.build(p); assert x['status']=='research_report_ready_read_only' and x['source_count']==1 and x['execution_started'] is False
 bad=Path(t)/'bad.jsonl'; bad.write_text('{bad\n',encoding='utf-8'); assert r.build(bad)['status']=='research_report_blocked'
print(json.dumps({'tests':2,'status':'passed','read_only_report':True,'automatic_execution':False},ensure_ascii=False))
