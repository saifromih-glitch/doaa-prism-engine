import json

from doaa_learning_registry import LearningRegistry

registry = LearningRegistry()
request = {"protocol": "doaa.alg.v1", "capability": "marketing.campaign", "slots": {"language": "ar"}}
result = {"protocol": "doaa.alg.v1", "authority": "none", "automatic_execution": False}
assert registry.record_experience("exp-1", "user-session", "2026-08-28T00:00:00Z", request, result, "user_allowed")["status"] == "experience_recorded"
assert registry.record_experience("exp-2", "web", "2026-08-28T00:00:00Z", request, result, "not_allowed")["reason"] == "consent_required"
message = {"protocol": "doaa.alg.v1", "algorithm": {"id": "marketing.campaign.v1", "version": "1"}, "authority": "none", "automatic_execution": False}
assert registry.propose_candidate("exp-1", "cand-1", "marketing.campaign", message)["status"] == "candidate_proposed"
assert registry.promote("cand-1", {"status": "passed"}, {"status": "passed"}, False)["reason"] == "human_approval_required"
assert registry.promote("cand-1", {"status": "pending"}, {"status": "passed"}, True)["reason"] == "evaluation_receipts_required"
assert registry.promote("cand-1", {"status": "passed", "version": "bench-1"}, {"status": "passed", "version": "safe-1"}, True)["status"] == "candidate_promoted"
active = registry.get_active("marketing.campaign")
assert active["status"] == "active_record_ready"
assert active["record"]["state"] == "active"
assert active["record"]["consent_status"] == "user_allowed"
assert registry.revoke("cand-1", "regression detected")["status"] == "active_record_revoked"
assert registry.get_active("marketing.campaign")["reason"] == "active_record_not_found"
assert registry.promote("cand-1", {"status": "passed"}, {"status": "passed"}, True)["reason"] == "candidate_not_found"
exported = registry.export()
assert exported["contract"] == "doaa.learning.v1"
assert exported["automatic_execution"] is False
print(json.dumps({"tests": 14, "status": "passed", "human_gate": True, "rollback": True, "consent_gate": True, "execution_authority": "none"}, ensure_ascii=False))
