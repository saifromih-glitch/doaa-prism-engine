import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import doaa_local_integration as m
ok = m.classify({"request_id":"req-1","payload":{"operation":"trim_ascii_spaces"},"execution_authority":"none"})
assert ok["status"] == "integration_message_accepted_for_governed_flow"
bad = m.classify({"request_id":"req-2","payload":{"shell":"dir"},"execution_authority":"none"})
assert bad["status"] == "integration_blocked"
extra = m.classify({"request_id":"req-3","payload":{},"execution_authority":"none","execute":True})
assert extra["status"] == "integration_blocked"
print(json.dumps({"tests":3,"status":"passed","commands_rejected":True,"automatic_execution":False}, ensure_ascii=False))
