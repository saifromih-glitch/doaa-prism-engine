import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_raw_proposal_boundary import verify_raw_boundary

base = {"status":"ollama_raw_proposal_received","message_id":"m1","model_id":"qwen-local","raw_response":"{\"kind\":\"proposal\"}","execution_authority":"none","automatic_execution":False,"execution_started":False,"writes_files":False,"source_modified":False,"network_scope":"local_ollama_only"}
assert verify_raw_boundary(base)["status"] == "raw_boundary_verified"
assert verify_raw_boundary({**base, "proposal": {}})["status"] == "raw_boundary_blocked"
assert verify_raw_boundary({**base, "execution_authority": "execute"})["reason"] == "authority_boundary_invalid"
assert verify_raw_boundary({**base, "status": "accepted_proposal"})["reason"] == "raw_result_required"
print({"tests":4,"status":"passed","raw_is_untrusted":True,"requires_gate":True,"automatic_execution":False})
