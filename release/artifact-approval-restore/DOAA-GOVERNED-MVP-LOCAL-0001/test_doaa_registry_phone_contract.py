import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_algorithm_registry import register,lookup
root=Path(__file__).parent/"test-runs-phone-contract"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True)
proposal={"operation":"remove_ascii_phone_separators","column":"phone","worksheet":None,"dsl_version":"1.4"}
review={"status":"accepted_by_human"}; receipt={"status":"executed_safe_file"}
ok=register(path,proposal,review,receipt)
assert ok["status"]=="registered" and ok["contract_id"]=="CONTRACT-DSL-PHONE-SEPARATORS-0001"
hit=lookup(path,proposal)
assert hit["status"]=="cache_hit" and hit["execution_authority"]=="none"
bad=register(root/"bad.jsonl",proposal,{"status":"pending_user_review"},receipt)
assert bad["status"]=="registry_rejected" and bad["reason"]=="human_acceptance_required"
print(json.dumps({"tests":4,"status":"passed","operation":"remove_ascii_phone_separators","contract_gate":"enforced"},ensure_ascii=False))
