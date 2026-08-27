import hashlib
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import doaa_audit_log as audit
import doaa_human_review as review

proposal = {"kind":"proposal","execution_authority":"none","operation":"normalize_ascii_spaces","column":"name","arguments":{},"rationale":"تنظيف محدود"}
gate = {"status":"accepted_proposal","execution_authority":"none","proposal":proposal}
with tempfile.TemporaryDirectory() as t:
    request = {"goal":"تنظيف الاسم","table_schema":[{"name":"name","type":"text"}],"dsl_version":"1.4","proposal":proposal}
    record = audit.make_record(request, '{"proposal":"raw"}', json.dumps(proposal, ensure_ascii=False), gate)
    assert record["gate_status"] == "accepted_proposal"
    assert record["execution_authority"] == "none" and record["dsl_execution"] is False
    result = review.review({"gate_result":gate,"decision":"accepted_by_human","explicit_confirmation":True,"audit_record":record,"audit_record_sha256":record["record_sha256"],"reviewer_note":"موافقة صريحة"})
    assert result["status"] == "accepted_by_human"
    assert result["proposal_sha256"] == hashlib.sha256(audit.canonical(proposal).encode("utf-8")).hexdigest()
    assert result["audit_record_sha256"] == record["record_sha256"]
    assert result["execution_started"] is False and result["execution_authority"] == "none"
    blocked = review.review({"gate_result":gate,"decision":"accepted_by_human","explicit_confirmation":False,"audit_record":record,"audit_record_sha256":record["record_sha256"]})
    assert blocked["reason"] == "explicit_decision_required"
    changed_gate = {"status":"accepted_proposal","execution_authority":"none","proposal":dict(proposal, column="phone")}
    changed = review.review({"gate_result":changed_gate,"decision":"accepted_by_human","explicit_confirmation":True,"audit_record":record,"audit_record_sha256":record["record_sha256"]})
    assert changed["reason"] == "audit_proposal_mismatch"
    wrong_hash = review.review({"gate_result":gate,"decision":"accepted_by_human","explicit_confirmation":True,"audit_record":record,"audit_record_sha256":"b"*64})
    assert wrong_hash["reason"] == "audit_hash_mismatch"
print(json.dumps({"tests":7,"status":"passed","audit_review_bound":True,"execution_authority":"none","execution_started":False}, ensure_ascii=False))
