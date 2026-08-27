import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_event_completeness import verify_completeness
events=["proposal_received","gate_checked","human_reviewed"]
args=(events,"a1","r1","abc","approved_for_governed_flow")
assert verify_completeness(*args)["status"] == "event_completeness_verified"
assert verify_completeness(events[:2],*args[1:])["status"] == "event_completeness_blocked"
assert verify_completeness(events+["human_reviewed"],*args[1:])["status"] == "event_completeness_blocked"
assert verify_completeness(["gate_checked","proposal_received","human_reviewed"],*args[1:])["status"] == "event_completeness_blocked"
assert verify_completeness(events,"","r1","abc","approved_for_governed_flow")["status"] == "event_completeness_blocked"
print(json.dumps({"tests":5,"status":"passed","complete":True,"automatic_execution":False}, ensure_ascii=False))
