import hashlib
import json
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[1]
test_root = root / "test-runs-excel"
input_path = test_root / "input-arabic-phone.xlsx"
output_path = test_root / "diagnostic-output.xlsx"
if output_path.exists():
    output_path.unlink()
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"الهاتف","arguments":{},"rationale":"safe"}
canon = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canon.encode()).hexdigest(),"audit_record_sha256":"d"*64}
payload = {"proposal":proposal,"human_review":review,"input_path":str(input_path),"output_path":str(output_path),"allowed_root":str(test_root),"worksheet":"البيانات"}
print("PROPOSAL_REPR", repr(proposal))
print("OP_OK", proposal.get("operation") == "remove_ascii_phone_separators")
print("COLUMN_OK", proposal.get("column") in {"phone", "الهاتف"})
print("ARGS_OK", proposal.get("arguments") == {})
with zipfile.ZipFile(input_path) as z:
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    print("SHEETS_REPR", [s.attrib.get("name") for s in wb.findall("m:sheets/m:sheet", ns)])
    print("WORKSHEET_REPR", repr(payload["worksheet"]))
source_lines = (root / "doaa_excel_safe_execute.py").read_text(encoding="utf-8").splitlines()
for i in range(66, 72):
    print("SOURCE_LINE", i + 1, repr(source_lines[i]))
proc = subprocess.run([sys.executable, str(root / "doaa_excel_safe_execute.py")], input=json.dumps(payload, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True)
print("RETURN_CODE", proc.returncode)
print("STDOUT", proc.stdout)
print("STDERR", proc.stderr)
print("INPUT_EXISTS", input_path.exists())
print("OUTPUT_EXISTS", output_path.exists())
