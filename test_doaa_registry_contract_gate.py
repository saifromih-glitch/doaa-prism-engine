import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_algorithm_registry import register,lookup
root=Path(__file__).parent/"test-runs-registry-contract-wire"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True)
proposal={"operation":"normalize_ascii_spaces","column":"name","worksheet":None,"dsl_version":"1.4"}
review={"status":"accepted_by_human"}; receipt={"status":"space_normalize_executed_safe_file"}
ok=register(path,proposal,review,receipt)
assert ok["status"]=="registered" and ok["contract_id"]=="CONTRACT-DSL-SPACE-NORMALIZE-0001"
hit=lookup(path,proposal)
assert hit["status"]=="cache_hit" and hit["record"]["contract_id"]=="CONTRACT-DSL-SPACE-NORMALIZE-0001"
contract=Path(__file__).parent/"CONTRACT-DSL-SPACE-NORMALIZE-0001.json"; backup=contract.read_text(encoding="utf-8")
try:
    d=json.loads(backup); d["automatic_execution"]=True; contract.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
    rejected=register(root/"bad.jsonl",proposal,review,receipt)
    assert rejected["status"]=="registry_rejected" and rejected["reason"]=="contract_verification_failed"
finally: contract.write_text(backup,encoding="utf-8")
print(json.dumps({"tests":3,"status":"passed","contract_gate":"enforced","automatic_execution":False},ensure_ascii=False))
