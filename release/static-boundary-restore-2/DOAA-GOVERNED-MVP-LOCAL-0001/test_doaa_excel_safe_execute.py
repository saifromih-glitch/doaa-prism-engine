import hashlib
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_excel_safe_execute.py"
TEST_ROOT = ROOT / "test-runs-excel"
INPUT = TEST_ROOT / "input-arabic-phone.xlsx"
OUTPUT = TEST_ROOT / "output-arabic-phone.xlsx"
if OUTPUT.exists(): OUTPUT.unlink()
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"الهاتف","arguments":{},"rationale":"safe"}
canon = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canon.encode()).hexdigest(),"audit_record_sha256":"d"*64}
payload = {"proposal":proposal,"human_review":review,"input_path":str(INPUT),"output_path":str(OUTPUT),"allowed_root":str(TEST_ROOT),"worksheet":"البيانات"}
p = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(payload),text=True,encoding="utf-8",capture_output=True,check=True)
result = json.loads(p.stdout)
assert result["status"] == "excel_executed_safe_file", (result, p.stderr)
assert result["target_column"] == "الهاتف"
assert result["changed_cell_count"] == 2
assert result["source_modified"] is False
with ZipFile(OUTPUT) as z:
    sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    notes = z.read("xl/worksheets/sheet2.xml").decode("utf-8")
assert "010123456" in sheet and "011222333" in sheet
assert "عميل اختبار 1" in sheet and "100" in sheet
assert "لا تعدل" in notes
blocked = dict(payload, worksheet="غير موجود", output_path=str(TEST_ROOT / "blocked-worksheet.xlsx"))
p2 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(blocked),text=True,encoding="utf-8",capture_output=True,check=True)
assert json.loads(p2.stdout)["reason"] == "worksheet_not_unique"
blocked_overwrite = dict(payload, output_path=str(INPUT))
p3 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(blocked_overwrite),text=True,encoding="utf-8",capture_output=True,check=True)
assert json.loads(p3.stdout)["reason"] == "output_policy_violation"
missing_column_proposal = dict(proposal, column="غير موجود")
missing_column = dict(payload, proposal=missing_column_proposal, output_path=str(TEST_ROOT / "blocked-column.xlsx"))
missing_canon = json.dumps(missing_column_proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
missing_column["human_review"] = dict(review, proposal_sha256=hashlib.sha256(missing_canon.encode()).hexdigest())
p4 = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(missing_column),text=True,encoding="utf-8",capture_output=True,check=True)
print(p4.stdout)
assert json.loads(p4.stdout)["reason"] in {"phone_header_not_unique", "proposal_not_allowed"}
print(json.dumps({"tests":4,"status":"passed","changed_cell_count":2,"other_worksheet_preserved":True,"rejection_cases":3,"source_modified":False},separators=(",",":")))
