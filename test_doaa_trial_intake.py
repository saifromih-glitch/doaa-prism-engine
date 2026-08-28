import json

from doaa_trial_intake import summarize, validate_trial_record

valid = {"participant_id": "p-001", "consent_feedback": True, "consent_learning": False, "real_task": True, "problem_present": True, "would_retry": True, "feedback": "الإجابة مفيدة لكنها احتاجت تحققاً."}
assert validate_trial_record(valid)["status"] == "trial_record_accepted"
assert validate_trial_record({**valid, "real_task": False})["status"] == "trial_record_blocked"
assert validate_trial_record({**valid, "consent_feedback": "yes"})["status"] == "trial_record_blocked"
assert validate_trial_record({"participant_id": "p-001"})["status"] == "trial_record_blocked"
summary = summarize([valid, {**valid, "participant_id": "p-002", "would_retry": False}, {**valid, "participant_id": "p-003"}])
assert summary["accepted"] == 3
assert summary["problem_count"] == 3
assert summary["success_threshold_met"] is True
assert summary["synthetic_records_included"] is False
print(json.dumps({"tests": 7, "status": "passed", "real_task_required": True, "synthetic_rejected": True, "execution_authority": "none"}, ensure_ascii=False))
