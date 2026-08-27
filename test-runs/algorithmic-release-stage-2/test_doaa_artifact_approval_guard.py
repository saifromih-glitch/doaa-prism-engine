import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_artifact_approval_guard import approve_artifact
base={"artifact_id":"a1","release_id":"r1","manifest_sha256":"abc","generated_at":"now","verification_status":"consistency_verified","execution_authority":"none","automatic_execution":False,"automatic_repair":False,"writes_files":False}
assert approve_artifact(base)["status"] == "artifact_approved_for_registration"
missing=dict(base);missing.pop("manifest_sha256")
assert approve_artifact(missing)["status"] == "artifact_approval_blocked"
invalid=dict(base);invalid["verification_status"]="unknown"
assert approve_artifact(invalid)["status"] == "artifact_approval_blocked"
danger=dict(base);danger["automatic_execution"]=True
assert approve_artifact(danger)["status"] == "artifact_approval_blocked"
extra=dict(base);extra["raw_response"]="secret"
assert approve_artifact(extra)["status"] == "artifact_approval_blocked"
print(json.dumps({"tests":5,"status":"passed","registration_authorized":False,"fail_closed":True}, ensure_ascii=False))
