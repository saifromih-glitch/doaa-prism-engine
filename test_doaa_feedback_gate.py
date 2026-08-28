import json

from doaa_feedback_gate import assess_feedback_for_candidate

positive = {"status": "learning_signal_ready", "usefulness_score": 5, "correctness_signal": "unknown", "requires_independent_evidence": False, "negative_signal": False}
assert assess_feedback_for_candidate(positive, "cand-1")["status"] == "feedback_supports_candidate"
assert assess_feedback_for_candidate(positive, "cand-1")["promotion_eligible"] is False
believed_true = {**positive, "correctness_signal": "believed_true", "requires_independent_evidence": True}
assert assess_feedback_for_candidate(believed_true, "cand-2")["status"] == "feedback_blocks_candidate"
assert assess_feedback_for_candidate(believed_true, "cand-2", "verified_true")["status"] == "feedback_supports_candidate"
false = {**positive, "usefulness_score": 1, "correctness_signal": "believed_false", "negative_signal": True}
assert assess_feedback_for_candidate(false, "cand-3", "verified_true")["status"] == "feedback_blocks_candidate"
assert assess_feedback_for_candidate(believed_true, "cand-2", "verified_false")["reason"] == "independent_evidence_conflict"
assert assess_feedback_for_candidate({"status": "feedback_blocked"}, "cand-1")["reason"] == "learning_signal_required"
assert assess_feedback_for_candidate(positive, "", "unverified")["reason"] == "candidate_id_invalid"
print(json.dumps({"tests": 8, "status": "passed", "usefulness_separate_from_truth": True, "promotion_never_automatic": True, "execution_authority": "none"}, ensure_ascii=False))
