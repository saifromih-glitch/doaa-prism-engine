import csv,hashlib,json,sys
import hashlib
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from doaa_trim_ascii_spaces_execute import execute
root=Path(__file__).parent / "encoding-trial-001"
root.mkdir(exist_ok=True)
inp=root/"input-bom.csv"; out=root/"output.csv"
out.unlink(missing_ok=True)
inp=root/"input-bom.csv"; out=root/"output.csv"
inp.write_bytes("الهاتف,الاسم,المبلغ\n 010-123 ,عميل,100\n".encode("utf-8-sig"))
proposal={"kind":"proposal","execution_authority":"none","operation":"trim_ascii_spaces","column":"الهاتف","arguments":{},"rationale":"encoding test"}
canonical=json.dumps(proposal,ensure_ascii=False,sort_keys=True,separators=(",",":"))
req={"input_path":str(inp),"output_path":str(out),"allowed_root":str(root),"proposal":proposal,"human_review":{"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"audit_record_sha256":"a"*64}}
r=execute(req)
assert r["status"]=="trim_ascii_spaces_executed_safe_file", r

assert r["changed_cell_count"]==1
assert "الهاتف" in out.read_text(encoding="utf-8")
print(json.dumps({"status":"passed","bom_input":True,"arabic_header":True,"changed_cell_count":1},ensure_ascii=False))




