import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_preview import preview
root=Path(__file__).parent/"preview-trial-001"; root.mkdir(exist_ok=True)
inp=root/"input.csv"; out=root/"should-not-exist.csv"
inp.write_text("الهاتف,الاسم\n 010-123 ,عميل\n",encoding="utf-8")
req={"input_path":str(inp),"output_path":str(out),"proposal":{"operation":"trim_ascii_spaces","column":"الهاتف"}}
r=preview(req)
assert r["status"]=="preview_ready" and r["changed_cell_count"]==1
assert r["samples"][0]["before"]==" 010-123 " and r["samples"][0]["after"]=="010-123"
assert not out.exists() and r["writes_files"] is False and r["execution_started"] is False
bad=preview({"input_path":str(inp),"proposal":{"operation":"unknown","column":"الهاتف"}})
assert bad["status"]=="preview_blocked"
print(json.dumps({"tests":4,"status":"passed","writes_files":False,"execution_started":False},ensure_ascii=False))

