import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_independent_evidence_verifier import verify
base={"state_summary":{"next_step":"next governed step"},"run_report":{"health_status":"health_ok","execution_authority":"none","automatic_execution":False,"automatic_repair":False},"health_report":{"status":"health_ok","execution_authority":"none","automatic_execution":False,"automatic_repair":False}}
assert verify(base)["status"] == "evidence_verified"
bad=dict(base);bad["run_report"]={**base["run_report"],"automatic_execution":True}
assert verify(bad)["status"] == "evidence_blocked"
mismatch=dict(base);mismatch["health_report"]={**base["health_report"],"status":"health_blocked"}
assert verify(mismatch)["status"] == "evidence_blocked"
extra=dict(base);extra["write_path"]="x"
assert verify(extra)["status"] == "evidence_blocked"
empty={"state_summary":{},"run_report":base["run_report"],"health_report":base["health_report"]}
assert verify(empty)["status"] == "evidence_blocked"
print(json.dumps({"tests":5,"status":"passed","independent":True,"read_only":True}, ensure_ascii=False))
