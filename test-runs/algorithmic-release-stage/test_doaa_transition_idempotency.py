import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_transition_idempotency import verify_idempotent_transition
valid=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]
assert verify_idempotent_transition(valid,["human_reviewed","approved_for_governed_flow"])["status"] == "idempotency_verified"
assert verify_idempotent_transition(valid+["approved_for_governed_flow"],["human_reviewed","approved_for_governed_flow"])["status"] == "idempotency_blocked"
assert verify_idempotent_transition(valid+["execution_started","execution_started"],["approved_for_governed_flow","execution_started"])["status"] == "idempotency_blocked"
assert verify_idempotent_transition(valid+["execution_started"],["approved_for_governed_flow","execution_started"])["status"] == "idempotency_blocked"
assert verify_idempotent_transition(valid+["gate_checked"],["proposal_received","gate_checked"])["status"] == "idempotency_blocked"
print(json.dumps({"tests":5,"status":"passed","single_application":True,"automatic_execution":False}, ensure_ascii=False))
