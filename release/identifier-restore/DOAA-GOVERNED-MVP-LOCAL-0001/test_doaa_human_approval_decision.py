import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_human_approval_decision import record_decision
ok=record_decision("a1","approve_for_governed_flow","r1","abc")
assert ok["status"] == "approved_for_governed_flow" and ok["execution_started"] is False and ok["automatic_execution"] is False
reject=record_decision("a1","reject","r1","abc")
assert reject["status"] == "rejected_by_human" and reject["execution_started"] is False
unknown=record_decision("a1","unknown","r1","abc")
assert unknown["status"] == "rejected_by_human"
empty=record_decision("","approve_for_governed_flow","r1","abc")
assert empty["status"] == "approval_blocked"
bad=record_decision("a1","approve_for_governed_flow","","abc")
assert bad["status"] == "approval_blocked"
print(json.dumps({"tests":5,"status":"passed","gate_only_accept":True,"default_reject":True}, ensure_ascii=False))
