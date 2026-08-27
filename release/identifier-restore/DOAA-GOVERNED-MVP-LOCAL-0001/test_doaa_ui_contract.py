import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_daily_ui import build_request
root=Path(__file__).parent/"ui-contract-trial"; root.mkdir(exist_ok=True)
inp=root/"input.csv"; out=root/"output.csv"; inp.write_text("الهاتف,الاسم\n 010-123 ,عميل\n",encoding="utf-8")
r=build_request(str(inp),str(out),"trim_ascii_spaces","الهاتف")
assert r["proposal"]["execution_authority"]=="none"
assert r["human_review"]["status"]=="pending_user_review" and r["human_review"]["execution_authority"]=="none"
assert r["execution_started"] is False and not out.exists()
r["human_review"]["preview_input_sha256"]="c"*64
assert r["human_review"]["preview_input_sha256"]=="c"*64
print(json.dumps({"tests":4,"status":"passed","execution_authority":"none","output_exists":out.exists()},ensure_ascii=False))
