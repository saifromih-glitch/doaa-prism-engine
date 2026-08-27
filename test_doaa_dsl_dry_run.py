import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_dsl_dry_run.py"
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"safe"}
review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":"a"*64,"audit_record_sha256":"b"*64}
rows = [{"name":"Ali  Hassan","phone":"010-123 456","amount":100},{"name":"Mona","phone":"011 222-333","amount":250}]

def run(payload):
    p = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(payload),text=True,encoding="utf-8",capture_output=True,check=True)
    return json.loads(p.stdout)

result = run({"proposal":proposal,"human_review":review,"rows":rows})
assert result["status"] == "dry_run_preview"
assert result["preview_rows"][0]["phone"] == "010123456"
assert result["preview_rows"][1]["phone"] == "011222333"
assert result["preview_rows"][0]["name"] == "Ali  Hassan"
assert result["preview_rows"][0]["amount"] == 100
assert result["changed_cell_count"] == 2
assert all(result["invariants"].values())
assert result["execution_started"] is False
assert result["source_modified"] is False
blocked = run({"proposal":proposal,"human_review":{"status":"review_blocked","execution_authority":"none"},"rows":rows})
assert blocked["status"] == "dry_run_blocked"
assert blocked["reason"] == "human_acceptance_required"
assert blocked["execution_started"] is False
print(json.dumps({"tests":2,"status":"passed","execution_started":False,"source_modified":False},separators=(",",":")))
