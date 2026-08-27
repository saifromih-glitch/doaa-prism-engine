import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_algorithm_registry import register,lookup
from doaa_dsl_contract_verifier import verify_contract
root=Path(__file__).parent/"test-runs-trim-contract"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True)
proposal={"operation":"trim_ascii_spaces","column":"name","worksheet":None,"dsl_version":"1.5"}
review={"status":"accepted_by_human"}; receipt={"status":"space_normalize_executed_safe_file"}
verified=verify_contract(Path(__file__).parent/"CONTRACT-DSL-TRIM-ASCII-SPACES-0001.json","trim_ascii_spaces")
assert verified["status"]=="contract_verified"
ok=register(path,proposal,review,receipt)
assert ok["status"]=="registered" and ok["contract_id"]=="CONTRACT-DSL-TRIM-ASCII-SPACES-0001"
hit=lookup(path,proposal)
assert hit["status"]=="cache_hit" and hit["record"]["contract_id"]=="CONTRACT-DSL-TRIM-ASCII-SPACES-0001"
bad=register(root/"bad.jsonl",dict(proposal,operation="trim_ascii_spaces"),{"status":"pending_user_review"},receipt)
assert bad["status"]=="registry_rejected" and bad["reason"]=="human_acceptance_required"
print(json.dumps({"tests":4,"status":"passed","trim_contract_gate":"enforced","execution_authority":"none"},ensure_ascii=False))

