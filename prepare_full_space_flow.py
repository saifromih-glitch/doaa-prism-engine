import hashlib
import json
from pathlib import Path

root = Path(r"C:\Users\saifr\OneDrive\Desktop\Doaa-Local\test-runs-full-space")
root.mkdir(exist_ok=True)
input_path = root / "input.csv"
output_path = root / "output.csv"
if output_path.exists(): output_path.unlink()
input_path.write_text("name,phone,amount\n  Ali   Hassan  ,010-123 456,100\nMona  Salem,011 222-333,250\n", encoding="utf-8", newline="")
proposal = {"kind":"proposal","execution_authority":"none","operation":"normalize_ascii_spaces","column":"name","arguments":{},"rationale":"Normalize ASCII spaces in name only."}
canon = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
payload = {"proposal":proposal,"human_review":{"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canon.encode("utf-8")).hexdigest(),"audit_record_sha256":"1"*64},"input_path":str(input_path),"output_path":str(output_path),"allowed_root":str(root)}
Path(__file__).with_name("full-space-flow-request.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
print(json.dumps({"status":"prepared","input":str(input_path),"output":str(output_path)}, ensure_ascii=False, separators=(",", ":")))
