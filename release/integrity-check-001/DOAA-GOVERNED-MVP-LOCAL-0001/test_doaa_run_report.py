import json,sys
sys.path.insert(0, r"C:\Users\saifr\OneDrive\Desktop\Doaa-Local")
import doaa_run_report as r
x=r.build({"status":"executed_safe_file","execution_started":True})
assert x["status"]=="run_report_ready" and x["automatic_execution"] is False
y=r.build({"status":"local_flow_blocked","blocked_at":"gate"})
assert y["summary_ar"]=="تم حجب الطلب بأمان"
print(json.dumps({"tests":2,"status":"passed","arabic_summary":True,"automatic_execution":False},ensure_ascii=False))
