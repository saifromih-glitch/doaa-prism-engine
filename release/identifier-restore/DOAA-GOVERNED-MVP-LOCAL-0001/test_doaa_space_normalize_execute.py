import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
TEST_ROOT = ROOT / "test-runs-space"
TEST_ROOT.mkdir(exist_ok=True)
INPUT = TEST_ROOT / "input.csv"
OUTPUT = TEST_ROOT / "output.csv"
for p in (OUTPUT,):
    if p.exists(): p.unlink()
INPUT.write_text("name,phone,amount\n  Ali   Hassan  ,010-123 456,100\nMona  Salem,011 222-333,250\n", encoding="utf-8", newline="")
proposal = {"kind":"proposal","execution_authority":"none","operation":"normalize_ascii_spaces","column":"name","arguments":{},"rationale":"normalize name spaces only"}
canon = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
payload = {"proposal":proposal,"human_review":{"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canon.encode()).hexdigest(),"audit_record_sha256":"a"*64},"input_path":str(INPUT),"output_path":str(OUTPUT),"allowed_root":str(TEST_ROOT)}
p = subprocess.run([sys.executable,str(ROOT / "doaa_space_normalize_execute.py")], input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True, check=True)
r = json.loads(p.stdout)
assert r["status"] == "space_normalize_executed_safe_file", r
assert r["changed_cell_count"] == 2
assert r["non_target_columns_changed"] == []
assert r["source_modified"] is False
assert OUTPUT.read_text(encoding="utf-8") == "name,phone,amount\nAli Hassan,010-123 456,100\nMona Salem,011 222-333,250\n"
blocked = dict(payload, output_path=str(TEST_ROOT / "blocked.csv"), human_review=dict(payload["human_review"], proposal_sha256="0"*64))
p2 = subprocess.run([sys.executable,str(ROOT / "doaa_space_normalize_execute.py")], input=json.dumps(blocked), text=True, encoding="utf-8", capture_output=True, check=True)
assert json.loads(p2.stdout)["reason"] == "proposal_hash_mismatch"
print(json.dumps({"tests":2,"status":"passed","target_column_isolated":True,"automatic_execution":False}, separators=(",", ":")))
