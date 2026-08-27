import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import doaa_web_research_gate as web
import doaa_local_integration as local
import doaa_model_mediation as med
cases = [
    web.gate({'source_url':'file:///secret','title':'x','excerpt':'x'}),
    local.classify({'request_id':'x','payload':{'shell':'dir'},'execution_authority':'none'}),
    med.classify({'message_id':'x','model_id':'m','proposal':{'source_code':'print(1)'},'execution_authority':'none'}),
    med.classify({'message_id':'x','model_id':'m','proposal':{},'execution_authority':'execute'})
]
assert all(x['status'].endswith('blocked') for x in cases)
assert all(x.get('execution_authority') == 'none' for x in cases)
print(json.dumps({'tests':4,'status':'passed','rejection_matrix':True,'automatic_execution':False},ensure_ascii=False))
