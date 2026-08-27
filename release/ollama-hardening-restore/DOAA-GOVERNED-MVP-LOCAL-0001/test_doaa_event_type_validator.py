import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_event_type_validator import validate_event_type
assert validate_event_type("proposal_received")["status"] == "event_type_verified"
assert validate_event_type("human_reviewed")["status"] == "event_type_verified"
assert validate_event_type("")["status"] == "event_type_blocked"
assert validate_event_type("unknown_event")["status"] == "event_type_blocked"
assert validate_event_type(None)["status"] == "event_type_blocked"
print(json.dumps({"tests":5,"status":"passed","known_type_only":True,"automatic_execution":False}, ensure_ascii=False))
