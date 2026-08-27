import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_dsl_contract_verifier import verify_contract
root=Path(__file__).parent/"contract-verifier-trial"; root.mkdir(exist_ok=True)
good=root/"good.json"; good.write_text((Path(__file__).parent/"CONTRACT-DSL-SPACE-NORMALIZE-0001.json").read_text(encoding="utf-8"),encoding="utf-8")
r=verify_contract(good,"normalize_ascii_spaces")
assert r["status"]=="contract_verified" and r["execution_authority"]=="none"
missing=root/"missing.json"; missing.write_text(json.dumps({"operation":"normalize_ascii_spaces"},ensure_ascii=False),encoding="utf-8")
r2=verify_contract(missing,"normalize_ascii_spaces")
assert r2["status"]=="contract_rejected" and r2["reason"]=="required_fields_missing"
bad=root/"bad.json"; d=json.loads(good.read_text(encoding="utf-8")); d["automatic_execution"]=True; bad.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
r3=verify_contract(bad,"normalize_ascii_spaces")
assert r3["status"]=="contract_rejected" and r3["reason"]=="governance_flags_invalid"
mismatch=verify_contract(good,"eval")
assert mismatch["status"]=="contract_rejected" and mismatch["reason"]=="operation_mismatch"
print(json.dumps({"tests":4,"status":"passed","verified":"normalize_ascii_spaces","unknown":"rejected"},ensure_ascii=False))


