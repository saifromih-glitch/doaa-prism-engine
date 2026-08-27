import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_algorithm_registry import register,lookup
from doaa_dsl_dry_run import run
root=Path(__file__).parent/"test-runs-registry-gate"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True)
proposal={"operation":"normalize_ascii_spaces","column":"name","worksheet":None,"dsl_version":"1.4"}
assert register(path,proposal,{"status":"accepted_by_human"},{"status":"space_normalize_executed_safe_file"})["status"]=="registered"
hit=lookup(path,proposal)
assert hit["status"]=="cache_hit" and hit["execution_authority"]=="none" and hit["automatic_execution"] is False
pending={"proposal":{"kind":"proposal","execution_authority":"none","operation":"normalize_ascii_spaces","column":"name","arguments":{}},"human_review":{"status":"pending_user_review","execution_authority":"none"},"rows":[{"name":"  عميل  ","phone":"010"}]}
blocked=run(pending)
assert blocked["status"]=="dry_run_blocked" and blocked["reason"]=="human_acceptance_required" and blocked["execution_started"] is False
print(json.dumps({"tests":3,"status":"passed","cache_hit_does_not_execute":True,"human_gate":"required"},ensure_ascii=False))
