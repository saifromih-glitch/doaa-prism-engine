import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_ollama_review_ui import review_decision
accepted = review_decision("accept_for_gate")
assert accepted["status"] == "accepted_for_gate" and accepted["execution_started"] is False and accepted["automatic_execution"] is False
rejected = review_decision("reject")
assert rejected["status"] == "rejected_by_human" and rejected["execution_started"] is False
unknown = review_decision("anything_else")
assert unknown["status"] == "rejected_by_human"
print(json.dumps({"tests":3,"status":"passed","default_reject":True,"gate_only_accept":True,"automatic_execution":False}, ensure_ascii=False))
