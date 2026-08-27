import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import doaa_model_mediation as m
ok=m.classify({'message_id':'msg-1','model_id':'ollama:qwen','proposal':{'operation':'normalize_ascii_spaces','column':'name'},'execution_authority':'none'})
assert ok['status']=='model_proposal_accepted_for_gate'
bad=m.classify({'message_id':'msg-2','model_id':'ollama:qwen','proposal':{'shell_command':'del *'},'execution_authority':'none'})
assert bad['status']=='model_mediation_blocked'
wrong=m.classify({'message_id':'msg-3','model_id':'ollama:qwen','proposal':{},'execution_authority':'execute'})
assert wrong['status']=='model_mediation_blocked'
for key in ('generated_code','network_instruction','arbitrary_file_operation'):
    blocked=m.classify({'message_id':'msg-'+key,'model_id':'ollama:qwen','proposal':{key:'x'},'execution_authority':'none'})
    assert blocked['status']=='model_mediation_blocked' and blocked['automatic_execution'] is False
print(json.dumps({'tests':6,'status':'passed','model_role':'proposal_assistant','automatic_execution':False,'generated_code_rejected':True},ensure_ascii=False))
