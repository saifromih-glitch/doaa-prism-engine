import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_artifact_release_consistency import verify_consistency
base={"artifact_id":"artifact-001","release_id":"DOAA-0001","manifest_sha256":"abc","execution_authority":"none","automatic_execution":False}
assert verify_consistency(base,"DOAA-0001","abc")["status"] == "consistency_verified"
old=dict(base);old["release_id"]="DOAA-0000"
assert verify_consistency(old,"DOAA-0001","abc")["status"] == "consistency_blocked"
hash_bad=dict(base);hash_bad["manifest_sha256"]="old"
assert verify_consistency(hash_bad,"DOAA-0001","abc")["status"] == "consistency_blocked"
auth=dict(base);auth["execution_authority"]="execute"
assert verify_consistency(auth,"DOAA-0001","abc")["status"] == "consistency_blocked"
extra=dict(base);extra["raw_response"]="secret"
assert verify_consistency(extra,"DOAA-0001","abc")["status"] == "consistency_verified"
print(json.dumps({"tests":5,"status":"passed","release_bound":True,"read_only":True}, ensure_ascii=False))
