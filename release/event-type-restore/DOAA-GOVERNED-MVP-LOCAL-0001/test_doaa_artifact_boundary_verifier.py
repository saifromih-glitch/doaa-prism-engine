import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_artifact_boundary_verifier import verify_boundary
base={"artifact_id":"a1","execution_authority":"none","automatic_execution":False,"automatic_repair":False,"writes_files":False}
assert verify_boundary(base)["status"] == "boundary_verified"
forbidden=dict(base);forbidden["secret"]="x"
assert verify_boundary(forbidden)["status"] == "boundary_blocked"
path=dict(base);path["write_path"]="x"
assert verify_boundary(path)["status"] == "boundary_blocked"
auth=dict(base);auth["execution_authority"]="execute"
assert verify_boundary(auth)["status"] == "boundary_blocked"
wrong=dict(base);wrong["automatic_repair"]=True
assert verify_boundary(wrong)["status"] == "boundary_blocked"
print(json.dumps({"tests":5,"status":"passed","secrets_blocked":True,"write_paths_blocked":True}, ensure_ascii=False))
