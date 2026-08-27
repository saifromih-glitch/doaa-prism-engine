import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_dsl_dry_run import run
from doaa_algorithm_registry import register,lookup
payload={"proposal":{"kind":"proposal","execution_authority":"none","operation":"normalize_unicode_whitespace","column":"name","arguments":{}},"human_review":{"status":"accepted_by_human","execution_authority":"none"},"rows":[{"name":"دعاء\u00a0محمد\u202fعلي","phone":"010"},{"name":"سارة\u2003عمر","phone":"011"}]}
r=run(payload)
assert r["status"]=="dry_run_preview" and r["preview_rows"][0]["name"]=="دعاء محمد علي" and r["preview_rows"][1]["name"]=="سارة\u2003عمر" and r["preview_rows"][0]["phone"]=="010" and r["execution_started"] is False
root=Path(__file__).parent/"test-runs-unicode-contract"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True); proposal={"operation":"normalize_unicode_whitespace","column":"name","worksheet":None,"dsl_version":"1.4"}; ok=register(path,proposal,{"status":"accepted_by_human"},{"status":"space_normalize_executed_safe_file"}); assert ok["status"]=="registered" and ok["contract_id"]=="CONTRACT-DSL-UNICODE-WHITESPACE-0001"; assert lookup(path,proposal)["status"]=="cache_hit"
print(json.dumps({"tests":3,"status":"passed","unicode_policy":"U+00A0,U+202F only","other_unicode_preserved":True},ensure_ascii=False))
