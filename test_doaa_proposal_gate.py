import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
GATE = ROOT / "doaa_proposal_gate.py"
REQUEST = {
    "goal": "أزل المسافات والشرطات من رقم الهاتف فقط",
    "table_schema": [{"name": "name", "type": "text"}, {"name": "phone", "type": "text"}, {"name": "amount", "type": "number"}],
    "dsl_version": "1.4"
}


def run(output, request=REQUEST):
    payload = json.dumps({"request": request, "model_output": output}, ensure_ascii=False)
    completed = subprocess.run([sys.executable, str(GATE)], input=payload, text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(completed.stdout)


def check(name, actual, expected):
    if actual.get("status") != expected:
        raise AssertionError((name, actual))


accepted = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"تحويل ضيق على عمود نصي واحد."}
check("accepted", run(accepted), "accepted_proposal")
check("unknown operation", run(dict(accepted, operation="invented_operation")), "rejected")
check("wrong column", run(dict(accepted, column="amount")), "rejected")
check("extra key", run(dict(accepted, extra="x")), "rejected")
check("authority", run(dict(accepted, execution_authority="execute")), "rejected")
check("new capability", run({"kind":"governed_capability_request","execution_authority":"none","requested_goal":"قدرة جديدة","rationale":"تحتاج عقدًا واختبارات."}), "accepted_capability_request")
check("malformed request", run(accepted, dict(REQUEST, extra="x")), "rejected")
print(json.dumps({"tests":7,"status":"passed","dsl_execution":False}, separators=(",", ":")))
