import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import doaa_web_research_gate as g
ok=g.gate({'source_url':'https://example.com/report','title':'Report','excerpt':'Evidence text'})
assert ok['status']=='web_source_accepted_read_only' and ok['execution_authority']=='none' and ok['execution_started'] is False
bad=g.gate({'source_url':'file:///secret','title':'Bad','excerpt':'x'})
assert bad['status']=='web_research_blocked'
extra=g.gate({'source_url':'https://example.com','title':'T','excerpt':'E','command':'run'})
assert extra['status']=='web_research_blocked'
print(json.dumps({'tests':3,'status':'passed','read_only':True,'result_to_execution':'forbidden'},ensure_ascii=False))
