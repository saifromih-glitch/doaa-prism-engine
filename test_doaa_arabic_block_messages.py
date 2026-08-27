import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_run_report import build
r=build({"status":"excel_execution_blocked","reason":"proposal_hash_mismatch","execution_started":False})
assert r["summary_ar"]=="تم حجب الطلب بأمان" and "المعاينة" in r["reason_ar"] and r["reason"]=="proposal_hash_mismatch"
r2=build({"status":"excel_executed_safe_file","execution_started":True})
assert r2["summary_ar"]=="تم التنفيذ الآمن بعد المراجعة البشرية" and r2["reason_ar"]==""
print(json.dumps({"tests":2,"status":"passed","arabic_reason":"ok"},ensure_ascii=False))
