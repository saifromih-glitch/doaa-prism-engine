import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_event_context_match import verify_event_context
event={"event_type":"gate_checked","request_id":"q1","artifact_id":"a1","release_id":"r1"}
assert verify_event_context(event,"q1","a1","r1")["status"] == "event_context_verified"
assert verify_event_context({**event,"request_id":"q2"},"q1","a1","r1")["status"] == "event_context_blocked"
assert verify_event_context({**event,"artifact_id":"a2"},"q1","a1","r1")["status"] == "event_context_blocked"
assert verify_event_context({**event,"release_id":"r2"},"q1","a1","r1")["status"] == "event_context_blocked"
assert verify_event_context({**event,"extra":"x"},"q1","a1","r1")["status"] == "event_context_blocked"
print(json.dumps({"tests":5,"status":"passed","exact_match":True,"automatic_execution":False}, ensure_ascii=False))
