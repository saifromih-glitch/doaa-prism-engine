import hashlib
import json
import sys
from datetime import datetime, timezone


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def review(payload):
    gate = payload.get("gate_result")
    decision = payload.get("decision")
    explicit = payload.get("explicit_confirmation") is True
    if not isinstance(gate, dict) or gate.get("status") != "accepted_proposal":
        return {"status": "review_blocked", "reason": "proposal_not_gate_accepted", "execution_started": False, "execution_authority": "none"}
    proposal = gate.get("proposal")
    if not isinstance(proposal, dict) or gate.get("execution_authority") != "none":
        return {"status": "review_blocked", "reason": "proposal_identity_invalid", "execution_started": False, "execution_authority": "none"}
    if decision not in {"accepted_by_human", "rejected_by_human"} or not explicit:
        return {"status": "review_blocked", "reason": "explicit_decision_required", "execution_started": False, "execution_authority": "none"}
    if not isinstance(payload.get("audit_record_sha256"), str) or len(payload["audit_record_sha256"]) != 64:
        return {"status": "review_blocked", "reason": "audit_identity_required", "execution_started": False, "execution_authority": "none"}
    result = {
        "contract_id": "CONTRACT-HUMAN-REVIEW-0001",
        "status": decision,
        "decision_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "proposal_sha256": sha256(canonical(proposal)),
        "audit_record_sha256": payload["audit_record_sha256"],
        "reviewer_note": payload.get("reviewer_note", ""),
        "execution_started": False,
        "execution_authority": "none",
        "source_modified": False,
        "network_request": False,
    }
    return result


def main():
    payload = json.loads(sys.stdin.read())
    print(canonical(review(payload)))


if __name__ == "__main__":
    main()
