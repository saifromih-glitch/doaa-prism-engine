import hashlib
import json
from pathlib import Path

path = Path(__file__).with_name("preflight-downloads.json")
payload = json.loads(path.read_text(encoding="utf-8"))
canonical = json.dumps(payload["proposal"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
payload["human_review"]["proposal_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
print(payload["human_review"]["proposal_sha256"])
