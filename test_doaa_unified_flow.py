import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_unified_flow.py"
TEST_ROOT = ROOT / "test-runs-unified"
TEST_ROOT.mkdir(exist_ok=True)
INPUT = TEST_ROOT / "input.csv"
OUTPUT = TEST_ROOT / "output.csv"
AUDIT = TEST_ROOT / "audit.jsonl"
for path in (INPUT, OUTPUT, AUDIT):
    if path.exists(): path.unlink()
INPUT.write_text("name,phone,amount\nTest One,010-123 456,100\nTest Two,011 222-333,250\n", encoding="utf-8", newline="")
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"Remove ASCII spaces and hyphens only from phone."}
payload = {"request":{"goal":"Remove separators from phone only","table_schema":[{"name":"name","type":"text"},{"name":"phone","type":"text"},{"name":"amount","type":"number"}],"dsl_version":"1.4"},"raw_model_text":json.dumps(proposal),"human_decision":"accepted_by_human","explicit_confirmation":True,"reviewer_note":"Test approval","audit_path":str(AUDIT),"input_path":str(INPUT),"output_path":str(OUTPUT),"allowed_root":str(TEST_ROOT)}
p = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(payload),text=True,encoding="utf-8",capture_output=True,check=True)
result = json.loads(p.stdout)
assert result["status"] == "flow_completed", result
assert result["gate_result"]["status"] == "accepted_proposal"
assert result["human_review"]["status"] == "accepted_by_human"
assert result["execution"]["status"] == "executed_safe_file"
assert result["execution"]["execution_started"] is True
assert result["execution"]["source_modified"] is False
assert result["execution"]["changed_cell_count"] == 2
assert AUDIT.is_file()
blocked = dict(payload, human_decision="accepted_by_human", explicit_confirmation=False, output_path=str(TEST_ROOT / "blocked.csv"))
p2 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(blocked),text=True,encoding="utf-8",capture_output=True,check=True)
b = json.loads(p2.stdout)
assert b["status"] == "flow_blocked"
assert b["blocked_at"] == "human_review"
assert b["execution_started"] is False
assert not (TEST_ROOT / "blocked.csv").exists()
records = [json.loads(line) for line in AUDIT.read_text(encoding="utf-8").splitlines() if line.strip()]
assert len(records) == 2 and all(item["dsl_execution"] is False and item["execution_authority"] == "none" for item in records)
print(json.dumps({"tests":4,"status":"passed","flow_completed":True,"rejected_flow_no_output":True,"audit_non_executable":True,"automatic_execution":False},separators=(",",":")))
