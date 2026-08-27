import hashlib
import json
from pathlib import Path

root = Path(r"C:\Users\saifr\OneDrive\Desktop\Doaa-Local\test-runs-safe")
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"Remove ASCII spaces and hyphens from phone only."}
canonical = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
proposal_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
payload = {
    "proposal": proposal,
    "human_review": {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":proposal_hash,"audit_record_sha256":"c"*64},
    "input_path": r"C:\Users\saifr\Downloads\Doaa-phone-test.csv",
    "output_path": str(root / "Doaa-phone-test-output.csv"),
    "allowed_root": str(root),
}
Path(__file__).with_name("user-test-execution-input.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
print(json.dumps({"status":"prepared","input":"Doaa-phone-test.csv","output":"Doaa-phone-test-output.csv"},separators=(",",":")))
