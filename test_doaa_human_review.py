import json
import subprocess
import sys
import doaa_audit_log as audit
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT = ROOT / "doaa_human_review.py"
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"safe"}
gate = {"status":"accepted_proposal","execution_authority":"none","proposal":proposal}

def run(decision, explicit, gate_value=gate):
    request = {"goal":"تنظيف الهاتف","table_schema":[{"name":"phone","type":"text"}],"dsl_version":"1.4","proposal":proposal}
    record = audit.make_record(request, "raw", json.dumps(proposal, ensure_ascii=False), gate_value)
    payload = {"gate_result":gate_value,"decision":decision,"explicit_confirmation":explicit,"audit_record":record,"audit_record_sha256":record["record_sha256"],"reviewer_note":"test"}
    p = subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps(payload),text=True,encoding="utf-8",capture_output=True,check=True)
    return json.loads(p.stdout)

accepted = run("accepted_by_human", True)
assert accepted["status"] == "accepted_by_human"
assert accepted["execution_started"] is False
assert accepted["execution_authority"] == "none"
assert accepted["source_modified"] is False
assert accepted["network_request"] is False
rejected = run("rejected_by_human", True)
assert rejected["status"] == "rejected_by_human"
blocked = run("accepted_by_human", False)
assert blocked["status"] == "review_blocked"
blocked_gate = run("accepted_by_human", True, {"status":"rejected","execution_authority":"none"})
assert blocked_gate["status"] == "review_blocked"
print(json.dumps({"tests":4,"status":"passed","execution_started":False,"source_modified":False},separators=(",",":")))
