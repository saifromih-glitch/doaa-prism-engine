import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_dsl_dry_run import run
from doaa_algorithm_registry import register,lookup
payload={"proposal":{"kind":"proposal","execution_authority":"none","operation":"tabs_to_ascii_space","column":"name","arguments":{}},"human_review":{"status":"accepted_by_human","execution_authority":"none"},"rows":[{"name":"دعاء\tمحمد","phone":"010"},{"name":"سارة","phone":"011"}]}
r=run(payload)
assert r["status"]=="dry_run_preview" and r["preview_rows"][0]["name"]=="دعاء محمد" and r["preview_rows"][0]["phone"]=="010" and r["execution_started"] is False
blocked=run(dict(payload,proposal=dict(payload["proposal"],arguments={"mode":"all"})))
assert blocked["status"]=="dry_run_blocked" and blocked["reason"]=="arguments_not_empty"
root=Path(__file__).parent/"test-runs-tabs-contract"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True); proposal={"operation":"tabs_to_ascii_space","column":"name","worksheet":None,"dsl_version":"1.4"}; ok=register(path,proposal,{"status":"accepted_by_human"},{"status":"executed_safe_file"}); assert ok["status"]=="registered" and ok["contract_id"]=="CONTRACT-DSL-TABS-TO-SPACE-0001"; assert lookup(path,proposal)["status"]=="cache_hit"
print(json.dumps({"tests":5,"status":"passed","operation":"tabs_to_ascii_space","execution_authority":"none"},ensure_ascii=False))
