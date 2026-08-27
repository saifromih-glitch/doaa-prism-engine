import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_trim_ascii_spaces_execute import execute, sha, canon
root=Path(__file__).parent/"stale-preview-trial"; root.mkdir(exist_ok=True)
inp=root/"input.csv"; out=root/"output.csv"; out.unlink(missing_ok=True)
inp.write_text("الهاتف,الاسم\n 010-123 ,أ\n",encoding="utf-8")
proposal={"kind":"proposal","execution_authority":"none","operation":"trim_ascii_spaces","column":"الهاتف","arguments":{},"rationale":"test"}
review={"status":"accepted_by_human","execution_authority":"none","proposal_sha256":sha(canon(proposal)),"audit_record_sha256":"a"*64,"preview_input_sha256":hashlib.sha256(inp.read_bytes()).hexdigest()}
inp.write_text("الهاتف,الاسم\n 010-999 ,أ\n",encoding="utf-8")
r=execute({"input_path":str(inp),"output_path":str(out),"allowed_root":str(root),"proposal":proposal,"human_review":review})
print(json.dumps(r,ensure_ascii=False)); assert not out.exists()
print(json.dumps({"tests":1,"status":"passed","reason":r["reason"],"output_exists":out.exists()},ensure_ascii=False))

