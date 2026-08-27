import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_algorithm_registry import register,lookup,lookup_all
root=Path(__file__).parent/"test-runs-registry-normalize"; root.mkdir(exist_ok=True); path=root/"algorithms.jsonl"; path.unlink(missing_ok=True)
proposal={"operation":"normalize_ascii_spaces","column":"name","worksheet":None,"dsl_version":"1.4"}
review={"status":"accepted_by_human"}
receipt={"status":"space_normalize_executed_safe_file"}
bad=register(path,proposal,{"status":"pending_user_review"},receipt)
assert bad["status"]=="registry_rejected" and bad["reason"]=="human_acceptance_required"
ok=register(path,proposal,review,receipt)
assert ok["status"]=="registered" and ok["automatic_execution"] is False
hit=lookup(path,proposal)
assert hit["status"]=="cache_hit" and hit["record"]["signature"]["operation"]=="normalize_ascii_spaces"
dup=register(path,proposal,review,receipt)
assert dup["status"]=="registry_duplicate"
assert len(lookup_all(path))==1
print(json.dumps({"tests":5,"status":"passed","cache":"hit","operation":"normalize_ascii_spaces","execution_authority":"none"},ensure_ascii=False))
