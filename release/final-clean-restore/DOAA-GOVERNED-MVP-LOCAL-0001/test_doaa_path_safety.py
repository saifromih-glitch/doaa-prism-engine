import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_path_safety import verify_path_safety
valid=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]
assert verify_path_safety(valid)["status"] == "path_verified"
assert verify_path_safety(valid[:3]+["execution_started"])["status"] == "path_blocked"
assert verify_path_safety(["proposal_received","execution_started","gate_checked","human_reviewed"])["status"] == "path_blocked"
assert verify_path_safety(["proposal_received","gate_checked"])["status"] == "path_blocked"
assert verify_path_safety(["gate_checked","proposal_received","human_reviewed"])["status"] == "path_blocked"
print(json.dumps({"tests":5,"status":"passed","gate_safe":True,"automatic_execution":False}, ensure_ascii=False))
