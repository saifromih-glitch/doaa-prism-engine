import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_event_identity import verify_event_identity
base=[{"event_type":"proposal_received","request_id":"q1","artifact_id":"a1","release_id":"r1"},{"event_type":"gate_checked","request_id":"q1","artifact_id":"a1","release_id":"r1"}]
assert verify_event_identity(base,"q1","a1","r1")["status"] == "event_identity_verified"
mixed=[*base,{"event_type":"human_reviewed","request_id":"q2","artifact_id":"a1","release_id":"r1"}]
assert verify_event_identity(mixed,"q1","a1","r1")["status"] == "event_identity_blocked"
wrong_shape=[{"event_type":"proposal_received","request_id":"q1","artifact_id":"a1"}]
assert verify_event_identity(wrong_shape,"q1","a1","r1")["status"] == "event_identity_blocked"
wrong_artifact=[{**base[0],"artifact_id":"a2"}]
assert verify_event_identity(wrong_artifact,"q1","a1","r1")["status"] == "event_identity_blocked"
assert verify_event_identity([],"q1","a1","r1")["status"] == "event_identity_verified"
print(json.dumps({"tests":5,"status":"passed","single_identity":True,"automatic_execution":False}, ensure_ascii=False))
