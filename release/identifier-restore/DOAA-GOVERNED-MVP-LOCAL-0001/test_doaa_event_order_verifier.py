import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_event_order_verifier import verify_event_order
valid=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]
assert verify_event_order(valid)["status"] == "event_order_verified"
assert verify_event_order(valid+["human_reviewed"])["status"] == "event_order_blocked"
assert verify_event_order(["gate_checked","proposal_received","human_reviewed"])["status"] == "event_order_blocked"
assert verify_event_order(["proposal_received","gate_checked","execution_started","human_reviewed"])["status"] == "event_order_blocked"
assert verify_event_order(["proposal_received","gate_checked"])["status"] == "event_order_blocked"
print(json.dumps({"tests":5,"status":"passed","ordered":True,"execution_before_review":False}, ensure_ascii=False))
