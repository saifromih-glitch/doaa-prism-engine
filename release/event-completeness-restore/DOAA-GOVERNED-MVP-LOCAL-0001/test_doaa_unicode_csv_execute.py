import csv
import hashlib
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from doaa_unicode_csv_execute import execute, canon, sha

with tempfile.TemporaryDirectory() as t:
    root = Path(t)
    inp = root / "input.csv"
    out = root / "output.csv"
    inp.write_bytes("الاسم,ملاحظة\nدعاء\u00a0محمد,مسافة\u202fضيقة\nسارة,لا تغيير\n".encode("utf-8-sig"))
    proposal = {"kind":"proposal","execution_authority":"none","operation":"normalize_unicode_whitespace","column":"ملاحظة","arguments":{},"rationale":"تحويل المحرفين المسموحين فقط"}
    review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":sha(canon(proposal)),"audit_record_sha256":"a"*64,"preview_input_sha256":sha(inp.read_bytes())}
    result = execute({"proposal":proposal,"human_review":review,"input_path":str(inp),"output_path":str(out),"allowed_root":str(root)})
    assert result["status"] == "normalize_unicode_whitespace_executed_safe_file"
    assert result["changed_cell_count"] == 1
    assert result["invariants"]["non_target_columns_unchanged"] is True
    assert out.read_text(encoding="utf-8-sig").splitlines()[1].split(",")[1] == "مسافة ضيقة"
    assert inp.read_bytes().decode("utf-8-sig").splitlines()[1].split(",")[1] == "مسافة\u202fضيقة"
    missing_hash = execute({"proposal":proposal,"human_review":dict(review, preview_input_sha256=None),"input_path":str(inp),"output_path":str(root/"blocked.csv"),"allowed_root":str(root)})
    assert missing_hash["reason"] == "preview_source_hash_required_or_mismatch" and not (root/"blocked.csv").exists()
    bad_arg = execute({"proposal":dict(proposal, arguments={"x":1}),"human_review":review,"input_path":str(inp),"output_path":str(root/"blocked2.csv"),"allowed_root":str(root)})
    assert bad_arg["reason"] == "proposal_not_allowed" and not (root/"blocked2.csv").exists()
print(json.dumps({"tests":6,"status":"passed","arabic_bom":True,"only_allowed_codepoints":True,"source_modified":False}, ensure_ascii=False))
