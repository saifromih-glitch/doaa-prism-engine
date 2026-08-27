import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_governed_chain_audit import audit_chain
artifact={"release_id":"r1","manifest_sha256":"abc"}
approval={"reviewed_release_id":"r1","reviewed_manifest_sha256":"abc","execution_authority":"none","execution_started":False}
gate={"release_id":"r1","manifest_sha256":"abc","execution_authority":"none","automatic_execution":False,"execution_started":False}
assert audit_chain(artifact,approval,gate)["status"] == "chain_verified"
old=dict(approval);old["reviewed_release_id"]="r0"
assert audit_chain(artifact,old,gate)["status"] == "chain_blocked"
bad_gate=dict(gate);bad_gate["manifest_sha256"]="old"
assert audit_chain(artifact,approval,bad_gate)["status"] == "chain_blocked"
started=dict(approval);started["execution_started"]=True
assert audit_chain(artifact,started,gate)["status"] == "chain_blocked"
auto=dict(gate);auto["automatic_execution"]=True
assert audit_chain(artifact,approval,auto)["status"] == "chain_blocked"
print(json.dumps({"tests":5,"status":"passed","single_chain":True,"execution_started":False}, ensure_ascii=False))
