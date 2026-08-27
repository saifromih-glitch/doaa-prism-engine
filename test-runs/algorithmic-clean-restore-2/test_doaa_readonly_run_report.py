import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_readonly_run_report import build_report
ok = build_report({"health_status":"health_ok","audit_summary":{"events":2},"generated_at":"2026-08-26T00:00:00Z"})
assert ok["status"] == "run_report_ready" and ok["writes_files"] is False and ok["scheduling"] is False
blocked = build_report({"health_status":"health_broken","audit_summary":{},"generated_at":"now"})
assert blocked["status"] == "run_report_blocked"
extra = build_report({"health_status":"health_ok","audit_summary":{},"generated_at":"now","write_path":"x"})
assert extra["status"] == "run_report_blocked"
empty = build_report({"health_status":"health_ok","audit_summary":{},"generated_at":""})
assert empty["status"] == "run_report_blocked"
print(json.dumps({"tests":4,"status":"passed","read_only":True,"scheduling":False,"automatic_repair":False}, ensure_ascii=False))
