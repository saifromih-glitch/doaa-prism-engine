import json
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_verification_artifact import build_artifact, write_artifact
valid={"status":"evidence_verified","execution_authority":"none","automatic_execution":False,"automatic_repair":False,"writes_files":False,"one_next_step":True}
ready=build_artifact(valid,"artifact-001","2026-08-26T00:00:00Z")
assert ready["status"] == "artifact_ready" and ready["artifact"]["verification"]["status"] == "evidence_verified"
assert "raw_response" not in json.dumps(ready, ensure_ascii=False)
with tempfile.TemporaryDirectory() as temp:
    out=Path(temp)/"evidence.json"
    written=write_artifact(out, ready)
    assert written["status"] == "artifact_written" and out.is_file()
blocked=build_artifact({**valid,"raw_response":"secret"},"artifact-002","now")
assert blocked["status"] == "artifact_blocked"
assert write_artifact("never-write.json", blocked)["status"] == "artifact_blocked"
bad=build_artifact(valid,"", "now")
assert bad["status"] == "artifact_blocked"
print(json.dumps({"tests":5,"status":"passed","redaction":True,"explicit_write_only":True}, ensure_ascii=False))
