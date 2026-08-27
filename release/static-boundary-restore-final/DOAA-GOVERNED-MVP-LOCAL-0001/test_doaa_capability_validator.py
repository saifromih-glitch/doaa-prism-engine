import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import doaa_capability_validator as v

with tempfile.TemporaryDirectory() as t:
    p = Path(t) / "contract.json"
    good = {"contract_id":"X","operation":"x","model_execution_authority":"none","automatic_execution":False,"fail_closed":True,"prohibited_actions":["exec","eval","subprocess","socket","network_request","secret_access","overwrite_input","execute_generated_code"]}
    p.write_text(json.dumps(good), encoding="utf-8")
    assert v.validate(p)["status"] == "capability_contract_verified"
    good["automatic_execution"] = True
    p.write_text(json.dumps(good), encoding="utf-8")
    assert v.validate(p)["status"] == "capability_contract_blocked"
print(json.dumps({"tests":2,"status":"passed","independent_read_only_check":True,"automatic_execution":False}, ensure_ascii=False))
