import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_state_transition_safety import verify_transition
assert verify_transition("proposal","gate")["status"] == "transition_verified"
assert verify_transition("gate","human_review")["status"] == "transition_verified"
assert verify_transition("human_review","approved")["status"] == "transition_verified"
assert verify_transition("approved","execution")["status"] == "transition_blocked"
assert verify_transition("unknown","execution")["status"] == "transition_blocked"
print(json.dumps({"tests":5,"status":"passed","safe":True,"automatic_execution":False}, ensure_ascii=False))
