import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_execution_receipt_binding import verify_receipt_binding
base={"artifact_id":"a1","release_id":"r1","manifest_sha256":"abc","approval_id":"p1","audited":True,"execution_completed":True,"execution_authority":"none"}
assert verify_receipt_binding(base,"a1","r1","abc","p1")["status"] == "receipt_binding_verified"
assert verify_receipt_binding({**base,"release_id":"r0"},"a1","r1","abc","p1")["status"] == "receipt_binding_blocked"
assert verify_receipt_binding({**base,"manifest_sha256":"old"},"a1","r1","abc","p1")["status"] == "receipt_binding_blocked"
assert verify_receipt_binding({**base,"audited":False},"a1","r1","abc","p1")["status"] == "receipt_binding_blocked"
assert verify_receipt_binding({**base,"execution_authority":"operator"},"a1","r1","abc","p1")["status"] == "receipt_binding_blocked"
print(json.dumps({"tests":5,"status":"passed","bound":True,"automatic_execution":False}, ensure_ascii=False))
