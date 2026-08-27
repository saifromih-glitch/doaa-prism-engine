import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_local.py"
TEST_ROOT = ROOT / "test-runs-package"
TEST_ROOT.mkdir(exist_ok=True)
input_path = TEST_ROOT / "input.csv"
output_path = TEST_ROOT / "output.csv"
for path in (input_path, output_path):
    if path.exists(): path.unlink()
input_path.write_text("name,phone,amount\nPackage Test,010-123 456,100\n", encoding="utf-8", newline="")
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"package test"}
import hashlib
canonical = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
payload = {"proposal":proposal,"human_review":{"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"audit_record_sha256":"e"*64},"input_path":str(input_path),"output_path":str(output_path),"allowed_root":str(TEST_ROOT)}
p = subprocess.run([sys.executable,str(SCRIPT)], input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True, check=True)
result = json.loads(p.stdout)
assert result["status"] == "local_flow_completed", result
assert result["diagnostics"]["status"] == "diagnostics_passed"
assert result["execution"]["status"] == "executed_safe_file"
assert result["execution"]["source_modified"] is False
assert output_path.read_text(encoding="utf-8") == "name,phone,amount\nPackage Test,010123456,100\n"
unsupported = dict(payload, input_path=str(TEST_ROOT / "input.txt"), output_path=str(TEST_ROOT / "unsupported.csv"))
(TEST_ROOT / "input.txt").write_text("data", encoding="utf-8")
p2 = subprocess.run([sys.executable,str(SCRIPT)], input=json.dumps(unsupported), text=True, encoding="utf-8", capture_output=True, check=True)
blocked = json.loads(p2.stdout)
assert blocked["status"] == "local_flow_blocked"
assert blocked["execution"]["reason"] == "unsupported_input_extension"
assert blocked["execution_started"] is False
print(json.dumps({"tests":2,"status":"passed","diagnostics_passed":True,"automatic_execution":False}, separators=(",", ":")))
