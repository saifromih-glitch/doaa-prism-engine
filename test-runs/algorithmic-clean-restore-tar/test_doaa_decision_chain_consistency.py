import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_decision_chain_consistency import verify_decision_chain
approval={"reviewed_release_id":"r1","reviewed_manifest_sha256":"abc","execution_authority":"none","execution_started":False}
chain={"status":"chain_verified","release_id":"r1","manifest_sha256":"abc"}
assert verify_decision_chain(approval,chain)["status"] == "decision_chain_verified"
old=dict(approval);old["reviewed_release_id"]="r0"
assert verify_decision_chain(old,chain)["status"] == "decision_chain_blocked"
hash_bad=dict(approval);hash_bad["reviewed_manifest_sha256"]="old"
assert verify_decision_chain(hash_bad,chain)["status"] == "decision_chain_blocked"
not_verified=dict(chain);not_verified["status"]="chain_blocked"
assert verify_decision_chain(approval,not_verified)["status"] == "decision_chain_blocked"
started=dict(approval);started["execution_started"]=True
assert verify_decision_chain(started,chain)["status"] == "decision_chain_blocked"
print(json.dumps({"tests":5,"status":"passed","decision_bound":True,"execution_started":False}, ensure_ascii=False))
