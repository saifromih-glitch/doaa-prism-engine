import hashlib
import json
from pathlib import Path
p=Path(__file__).with_name("excel-test-input.json")
data=json.loads(p.read_text(encoding="utf-8"))
proposal=json.dumps(data["proposal"],ensure_ascii=False,sort_keys=True,separators=(",",":"))
data["human_review"]["proposal_sha256"]=hashlib.sha256(proposal.encode()).hexdigest()
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8",newline="\n")
print(data["human_review"]["proposal_sha256"])
