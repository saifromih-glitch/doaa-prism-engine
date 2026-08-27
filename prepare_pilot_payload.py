import hashlib
import json
from pathlib import Path

root = Path(r"C:\Users\saifr\OneDrive\Desktop\Doaa-Local\test-runs-pilot")
root.mkdir(exist_ok=True)
proposal = {
    "kind": "proposal",
    "execution_authority": "none",
    "operation": "remove_ascii_phone_separators",
    "column": "phone",
    "arguments": {},
    "rationale": "Remove ASCII spaces and hyphens from phone only."
}
canonical = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
payload = {
    "proposal": proposal,
    "human_review": {
        "status": "accepted_by_human",
        "execution_authority": "none",
        "proposal_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "audit_record_sha256": "f" * 64
    },
    "input_path": r"C:\Users\saifr\Downloads\Doaa-phone-test.csv",
    "output_path": str(root / "Doaa-phone-test-pilot-output.csv"),
    "allowed_root": str(root)
}
Path(__file__).with_name("pilot-request.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
print(json.dumps({"status":"prepared","input":payload["input_path"],"output":payload["output_path"]}, ensure_ascii=False, separators=(",", ":")))
