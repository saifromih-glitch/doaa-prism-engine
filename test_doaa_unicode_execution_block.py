import hashlib
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from doaa_safe_file_execute import execute

with tempfile.TemporaryDirectory() as t:
    root = Path(t)
    input_path = root / "input.csv"
    output_path = root / "output.csv"
    input_path.write_text("name,phone\nدعاء\u00a0محمد,010-123\n", encoding="utf-8-sig", newline="")
    proposal = {"kind":"proposal","execution_authority":"none","operation":"normalize_unicode_whitespace","column":"name","arguments":{},"rationale":"preview only"}
    canonical = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = {"proposal": proposal, "human_review": {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"audit_record_sha256":"a"*64}, "input_path":str(input_path),"output_path":str(output_path),"allowed_root":str(root)}
    result = execute(payload)
    assert result["status"] == "execution_blocked"
    assert result["reason"] == "proposal_not_allowed"
    assert result["execution_started"] is False
    assert not output_path.exists()
print(json.dumps({"tests":4,"status":"passed","unicode_operation_execution":"blocked","output_created":False}, ensure_ascii=False))
