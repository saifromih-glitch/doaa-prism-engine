import json
import sys
from pathlib import Path

from doaa_proposal_repair import repair_and_validate
from doaa_audit_log import make_record, append_record
from doaa_human_review import review
from doaa_safe_file_execute import execute as safe_execute


def run(payload):
    request = payload.get("request")
    raw = payload.get("raw_model_text")
    gate = repair_and_validate(raw, request)
    if gate.get("status") != "accepted_proposal":
        return {"status":"flow_blocked","blocked_at":"deterministic_gate","gate_result":gate,"execution_started":False}
    audit = make_record(request, raw, gate.get("repaired_model_text", raw), gate, gate.get("repair_id"))
    audit_path = Path(payload["audit_path"])
    append_record(audit_path, audit)
    human_payload = {
        "gate_result": gate,
        "decision": payload.get("human_decision"),
        "explicit_confirmation": payload.get("explicit_confirmation"),
        "audit_record": audit,
        "audit_record_sha256": audit["record_sha256"],
        "reviewer_note": payload.get("reviewer_note", ""),
    }
    human = review(human_payload)
    if human.get("status") != "accepted_by_human":
        return {"status":"flow_blocked","blocked_at":"human_review","gate_result":gate,"audit_record":audit,"human_review":human,"execution_started":False}
    execution_payload = {
        "proposal": gate["proposal"],
        "human_review": human,
        "input_path": payload["input_path"],
        "output_path": payload["output_path"],
        "allowed_root": payload["allowed_root"],
    }
    execution = safe_execute(execution_payload)
    return {"status":"flow_completed" if execution.get("status") == "executed_safe_file" else "flow_blocked","gate_result":gate,"audit_record":audit,"human_review":human,"execution":execution,"execution_started":execution.get("execution_started", False)}


def main():
    print(json.dumps(run(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__": main()
