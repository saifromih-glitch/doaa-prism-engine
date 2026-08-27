import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_execution_state_consistency import verify_execution_state
valid=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]
assert verify_execution_state(valid,"not_started")["status"] == "execution_state_verified"
assert verify_execution_state(valid,"ready_for_separate_safe_executor")["status"] == "execution_state_verified"
assert verify_execution_state(valid[:3],"not_started")["status"] == "execution_state_blocked"
assert verify_execution_state(valid+["execution_started"],"ready_for_separate_safe_executor")["status"] == "execution_state_blocked"
assert verify_execution_state(["proposal_received","gate_checked","approved_for_governed_flow","human_reviewed"],"not_started")["status"] == "execution_state_blocked"
print(json.dumps({"tests":5,"status":"passed","consistent":True,"automatic_execution":False}, ensure_ascii=False))
