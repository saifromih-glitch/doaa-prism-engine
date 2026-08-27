import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_safe_file_execute.py"
TEST_ROOT = ROOT / "test-runs-safe"
TEST_ROOT.mkdir(exist_ok=True)
INPUT = TEST_ROOT / "input.csv"
OUTPUT = TEST_ROOT / "output.csv"
for path in (OUTPUT, TEST_ROOT / "blocked.csv", TEST_ROOT / "external-no-phone.csv"):
    if path.exists(): path.unlink()
INPUT.write_text("name,phone,amount\nAli,010-123 456,100\nMona,011 222-333,250\n", encoding="utf-8", newline="")
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"safe"}
def canon(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
proposal_hash = hashlib.sha256(canon(proposal).encode()).hexdigest()
review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":proposal_hash,"audit_record_sha256":"b"*64}
payload = {"proposal":proposal,"human_review":review,"input_path":str(INPUT),"output_path":str(OUTPUT),"allowed_root":str(TEST_ROOT)}
p = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(payload),text=True,encoding="utf-8",capture_output=True,check=True)
result = json.loads(p.stdout)
assert result["status"] == "executed_safe_file"
assert result["comparison_result"] == "passed"
assert result["changed_cell_count"] == 2
assert result["source_modified"] is False
with INPUT.open(encoding="utf-8", newline="") as h: before = list(csv.DictReader(h))
with OUTPUT.open(encoding="utf-8", newline="") as h: after = list(csv.DictReader(h))
assert before[0]["phone"] == "010-123 456"
assert after[0]["phone"] == "010123456"
assert [r["name"] for r in before] == [r["name"] for r in after]
assert [r["amount"] for r in before] == [r["amount"] for r in after]
blocked = dict(payload, output_path=str(INPUT))
p2 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(blocked),text=True,encoding="utf-8",capture_output=True,check=True)
assert json.loads(p2.stdout)["reason"] == "input_output_policy_violation"
blocked_hash = dict(payload, output_path=str(TEST_ROOT / "blocked.csv"), human_review=dict(review, proposal_sha256="0"*64))
p3 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(blocked_hash),text=True,encoding="utf-8",capture_output=True,check=True)
assert json.loads(p3.stdout)["reason"] == "proposal_hash_mismatch"
external = dict(payload, input_path=r"C:\Users\saifr\Downloads\تقرير-ترشيح-فنادق-مكة-2026-08-19.csv", output_path=str(TEST_ROOT / "external-no-phone.csv"))
p4 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(external),text=True,encoding="utf-8",capture_output=True,check=True)
assert json.loads(p4.stdout)["reason"] == "target_column_missing"
assert not (TEST_ROOT / "external-no-phone.csv").exists()
print(json.dumps({"tests":4,"status":"passed","source_modified":False,"real_user_data_used":False},separators=(",",":")))
