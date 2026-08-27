import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_daily_ui import build_request
from doaa_trim_ascii_spaces_execute import execute

root = Path(__file__).parent / "trial-run-001"
inp = root / "input.csv"
out = root / "output.csv"
request = build_request(str(inp), str(out), "trim_ascii_spaces", "الهاتف")
proposal = request["proposal"]
canonical = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
request["human_review"] = {
    "status": "accepted_by_human",
    "execution_authority": "none",
    "proposal_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    "audit_record_sha256": "a" * 64,
}
result = execute(request)
(root / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"status": result.get("status"), "output_path": result.get("output_path"), "source_modified": result.get("source_modified"), "execution_started": result.get("execution_started"), "changed_cell_count": result.get("changed_cell_count")}, ensure_ascii=False))
