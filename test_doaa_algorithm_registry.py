import json
from pathlib import Path
from doaa_algorithm_registry import lookup, register

ROOT = Path(__file__).parent
path = ROOT / "test-runs-registry" / "algorithms.jsonl"
path.parent.mkdir(exist_ok=True)
if path.exists(): path.unlink()
proposal = {"operation":"remove_ascii_phone_separators","column":"phone","worksheet":None,"dsl_version":"1.4"}
review = {"status":"accepted_by_human"}
receipt = {"status":"executed_safe_file"}
registered = register(path, proposal, review, receipt)
assert registered["status"] == "registered", registered
hit = lookup(path, proposal)
assert hit["status"] == "cache_hit", hit
assert hit["execution_authority"] == "none"
assert hit["automatic_execution"] is False
miss = lookup(path, dict(proposal, column="mobile"))
assert miss["status"] == "cache_miss"
rejected = register(path, dict(proposal, column="email"), {"status":"pending_user_review"}, receipt)
assert rejected["status"] == "registry_rejected"
assert rejected["reason"] == "human_acceptance_required"
duplicate = register(path, proposal, review, receipt)
assert duplicate["status"] == "registry_duplicate"
lines = path.read_text(encoding="utf-8").splitlines()
assert len(lines) == 1
record = json.loads(lines[0])
assert record["record_type"] == "approved_algorithm"
assert record["execution_authority"] == "none"
print(json.dumps({"tests":5,"status":"passed","exact_match_only":True,"automatic_execution":False}, separators=(",", ":")))
