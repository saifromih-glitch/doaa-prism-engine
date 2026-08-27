import json
import subprocess
import sys
from pathlib import Path
from doaa_algorithm_registry import register

ROOT = Path(__file__).parent
REG = ROOT / "test-runs-registry" / "router.jsonl"
REG.parent.mkdir(exist_ok=True)
if REG.exists(): REG.unlink()
proposal = {"operation":"remove_ascii_phone_separators","column":"phone","worksheet":None,"dsl_version":"1.4"}
register(REG, proposal, {"status":"accepted_by_human"}, {"status":"executed_safe_file"})

def route(p):
    r = subprocess.run([sys.executable, str(ROOT / "doaa_premodel_router.py")], input=json.dumps(p), text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(r.stdout)
hit = route({"registry_path":str(REG),"proposal":proposal})
assert hit["route"] == "reuse_candidate" and hit["model_call"] is False and hit["automatic_execution"] is False
miss = route({"registry_path":str(REG),"proposal":dict(proposal, column="name")})
assert miss["route"] == "governed_model_stage" and miss["model_call"] is True and miss["automatic_execution"] is False
blocked = route({"registry_path":str(REG),"proposal":None})
assert blocked["route"] == "blocked" and blocked["model_call"] is False
print(json.dumps({"tests":3,"status":"passed","cache_hit_skips_model":True,"cache_miss_is_governed":True,"automatic_execution":False}, separators=(",", ":")))
