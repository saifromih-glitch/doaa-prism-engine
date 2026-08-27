import hashlib
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import doaa_premodel_router as router
import doaa_model_mediation as mediation
import doaa_web_research_gate as web_gate
import doaa_capability_advisor as advisor
import doaa_readonly_monitor as monitor
import doaa_local_integration as local_integration

with tempfile.TemporaryDirectory() as t:
    root=Path(t); registry=root/'registry.jsonl'; registry.write_text('',encoding='utf-8')
    route=router.route({'registry_path':str(registry),'proposal':{'operation':'unknown','column':'x'}})
    assert route['route']=='governed_model_stage'
    med=mediation.classify({'message_id':'m1','model_id':'local:test','proposal':{'operation':'unknown'},'execution_authority':'none'})
    assert med['status']=='model_proposal_accepted_for_gate'
    web=web_gate.gate({'source_url':'https://example.com','title':'T','excerpt':'E'})
    assert web['status']=='web_source_accepted_read_only' and web['execution_started'] is False
    adv=advisor.advise({'goal':'build a self modifying agent'})
    assert adv['status']=='governed_capability_request' and adv['automatic_execution'] is False
    integ=local_integration.classify({'request_id':'r1','payload':{'proposal':'x'},'execution_authority':'none'})
    assert integ['status']=='integration_message_accepted_for_governed_flow'
    man=root/'manifest.json'; man.write_text(json.dumps({'files':[]}),encoding='utf-8')
    mon=monitor.monitor(root,man)
    assert mon['status']=='monitor_ok' and mon['repair_started'] is False
print(json.dumps({'tests':6,'status':'passed','full_chain_verified':True,'automatic_execution':False,'model_authority':'none'},ensure_ascii=False))
