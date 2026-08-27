import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_terminal_state_safety import verify_terminal_state
events=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]
ready={"audited":False,"execution_authority":"none","execution_completed":False}
good={"audited":True,"execution_authority":"none","execution_completed":True}
assert verify_terminal_state(events,good)["status"] == "terminal_state_verified"
assert verify_terminal_state(events,ready)["status"] == "terminal_state_blocked"
assert verify_terminal_state(events,{"audited":False,"execution_authority":"none","execution_completed":True})["status"] == "terminal_state_blocked"
assert verify_terminal_state(events,{"audited":True,"execution_authority":"operator","execution_completed":True})["status"] == "terminal_state_blocked"
assert verify_terminal_state(events[:3],good)["status"] == "terminal_state_blocked"
print(json.dumps({"tests":5,"status":"passed","receipt_audited":True,"automatic_execution":False}, ensure_ascii=False))
