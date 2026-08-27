import json
import subprocess
import sys
from pathlib import Path
from doaa_algorithm_registry import register

ROOT = Path(__file__).parent
REG = ROOT / "test-runs-registry" / "retrieval.jsonl"
REG.parent.mkdir(exist_ok=True)
if REG.exists(): REG.unlink()
proposal = {"operation":"remove_ascii_phone_separators","column":"phone","worksheet":None,"dsl_version":"1.4"}
register(REG, proposal, {"status":"accepted_by_human"}, {"status":"executed_safe_file"})

def call(p):
    run = subprocess.run([sys.executable, str(ROOT / "doaa_deterministic_retrieval.py")], input=json.dumps(p), text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(run.stdout)
hit = call({"registry_path":str(REG),"proposal":proposal})
assert hit["status"] == "cache_hit", hit
assert hit["model_call"] is False
assert hit["automatic_execution"] is False
miss = call({"registry_path":str(REG),"proposal":dict(proposal, column="mobile")})
assert miss["status"] == "cache_miss", miss
assert miss["model_call"] is False
assert miss["execution_authority"] == "none"
blocked = call({"registry_path":str(REG),"proposal":None})
assert blocked["status"] == "retrieval_blocked"
assert blocked["model_call"] is False
print(json.dumps({"tests":3,"status":"passed","exact_signature_only":True,"model_calls":0,"automatic_execution":False}, separators=(",", ":")))
