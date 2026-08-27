import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_dsl_execute_test.py"
TEST_ROOT = ROOT / "test-runs"
INPUT = TEST_ROOT / "input-fixture.csv"
OUTPUT = TEST_ROOT / "output-fixture.csv"
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"safe"}
review = {"status":"accepted_by_human","execution_authority":"none"}
payload = {"mode":"explicit_test","proposal":proposal,"human_review":review,"input_path":str(INPUT),"output_path":str(OUTPUT),"allowed_root":str(TEST_ROOT)}
p = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(payload),text=True,encoding="utf-8",capture_output=True,check=True)
result = json.loads(p.stdout)
assert result["status"] == "executed_test_only"
assert result["execution_started"] is True
assert result["source_modified"] is False
assert result["non_target_columns_unchanged"] is True
assert result["changed_cell_count"] == 2
with INPUT.open(encoding="utf-8", newline="") as h:
    before = list(csv.DictReader(h))
with OUTPUT.open(encoding="utf-8", newline="") as h:
    after = list(csv.DictReader(h))
assert before[0]["phone"] == "010-123 456"
assert after[0]["phone"] == "010123456"
assert [r["name"] for r in before] == [r["name"] for r in after]
assert [r["amount"] for r in before] == [r["amount"] for r in after]
blocked_payload = dict(payload, output_path=str(ROOT / "outside-output.csv"))
p2 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(blocked_payload),text=True,encoding="utf-8",capture_output=True,check=True)
blocked = json.loads(p2.stdout)
assert blocked["status"] == "execution_blocked"
assert blocked["reason"] == "path_outside_test_root"
print(json.dumps({"tests":2,"status":"passed","output_created":True,"real_user_data_used":False},separators=(",",":")))
