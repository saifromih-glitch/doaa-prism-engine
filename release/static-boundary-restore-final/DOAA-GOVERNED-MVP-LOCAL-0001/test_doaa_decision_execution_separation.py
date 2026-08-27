import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_decision_execution_separation import verify_separation
ok=verify_separation({"status":"approved_for_governed_flow","execution_authority":"none","automatic_execution":False,"execution_started":False})
assert ok["status"] == "separation_verified" and ok["gate_only"] is True
reject=verify_separation({"status":"rejected_by_human","execution_authority":"none","automatic_execution":False,"execution_started":False})
assert reject["status"] == "separation_verified"
auto=verify_separation({"status":"approved_for_governed_flow","execution_authority":"execute","automatic_execution":True,"execution_started":True})
assert auto["status"] == "separation_blocked"
unknown=verify_separation({"status":"execute_now","execution_authority":"none","automatic_execution":False,"execution_started":False})
assert unknown["status"] == "separation_blocked"
assert verify_separation(None)["status"] == "separation_blocked"
print(json.dumps({"tests":5,"status":"passed","gate_only":True,"execution_started":False}, ensure_ascii=False))
