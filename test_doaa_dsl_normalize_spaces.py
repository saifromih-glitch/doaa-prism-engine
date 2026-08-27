import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_dsl_dry_run import run
def p(op,col,rows,args={}): return {"proposal":{"kind":"proposal","execution_authority":"none","operation":op,"column":col,"arguments":args},"human_review":{"status":"accepted_by_human","execution_authority":"none"},"rows":rows}
r=run(p("normalize_ascii_spaces","name",[{"name":"  عميل   أول ","phone":"010"},{"name":"سليم","phone":"011"}]))
assert r["status"]=="dry_run_preview" and r["preview_rows"][0]["name"]==" عميل أول " and r["changed_cell_count"]==1 and r["execution_started"] is False
old=run(p("remove_ascii_phone_separators","phone",[{"name":"عميل","phone":"010-123 456"}]))
assert old["status"]=="dry_run_preview" and old["preview_rows"][0]["phone"]=="010123456"
bad=run(p("normalize_ascii_spaces","name",[{"name":"  عميل  "}],{"pattern":"x"}))
assert bad["status"]=="dry_run_blocked" and bad["reason"]=="arguments_not_empty"
unsupported=run(p("eval","name",[{"name":"x"}]))
assert unsupported["status"]=="dry_run_blocked" and unsupported["reason"]=="operation_or_column_not_allowed"
print(json.dumps({"tests":4,"status":"passed","new_operation":"normalize_ascii_spaces","execution_authority":"none"},ensure_ascii=False))
