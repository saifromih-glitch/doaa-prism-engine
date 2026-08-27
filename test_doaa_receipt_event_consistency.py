import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_receipt_event_consistency import verify_receipt_events
types=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow","execution_started","execution_completed"]
base={"request_id":"q1","artifact_id":"a1","release_id":"r1","manifest_sha256":"abc"}
events=[{**base,"event_type":t} for t in types]
receipt={**base,"audited":True,"execution_completed":True,"execution_authority":"none"}
assert verify_receipt_events(receipt,events)["status"] == "receipt_events_verified"
assert verify_receipt_events(receipt,[{**events[0],"artifact_id":"a2"},*events[1:]])["status"] == "receipt_events_blocked"
assert verify_receipt_events(receipt,events[:-1])["status"] == "receipt_events_blocked"
assert verify_receipt_events(receipt,[*events[1:],events[0]])["status"] == "receipt_events_blocked"
assert verify_receipt_events({**receipt,"audited":False},events)["status"] == "receipt_events_blocked"
print(json.dumps({"tests":5,"status":"passed","identity_bound":True,"ordered":True}, ensure_ascii=False))
