import json

from doaa_feedback import FeedbackStore

store = FeedbackStore()
base = {"feedback_id": "fb-1", "interaction_id": "int-1", "usefulness": 5, "correctness_signal": "believed_true", "consent_to_learning": True, "created_at": "2026-08-28T00:00:00Z", "reason": "الإجابة واضحة"}
assert store.submit(base)["status"] == "feedback_recorded"
assert store.submit({**base, "feedback_id": "fb-2", "consent_to_learning": False})["learning_eligible"] is False
assert store.assess_learning_signal("fb-1")["status"] == "learning_signal_ready"
assert store.assess_learning_signal("fb-1")["truth_verified"] is False
assert store.assess_learning_signal("fb-1")["requires_independent_evidence"] is True
assert store.submit({**base, "feedback_id": "fb-3", "interaction_id": "int-3", "usefulness": 1, "correctness_signal": "believed_false"})["status"] == "feedback_recorded"
negative = store.assess_learning_signal("fb-3")
assert negative["negative_signal"] is True
assert store.submit({**base, "feedback_id": "fb-4", "interaction_id": "int-4", "correctness_signal": "needs_verification"})["status"] == "feedback_recorded"
assert store.assess_learning_signal("fb-4")["requires_independent_evidence"] is True
assert store.assess_learning_signal("fb-2")["status"] == "learning_signal_blocked"
assert store.submit({**base, "feedback_id": "fb-5", "interaction_id": "int-5", "usefulness": 6})["reason"] == "usefulness_invalid"
assert store.submit({**base, "feedback_id": "fb-6", "interaction_id": "int-6", "correctness_signal": "certainly_true"})["reason"] == "correctness_signal_invalid"
assert store.delete("fb-1")["status"] == "feedback_deleted"
assert store.assess_learning_signal("fb-1")["reason"] == "feedback_not_found"
assert store.export()["contract"] == "doaa.feedback.v1"
print(json.dumps({"tests": 14, "status": "passed", "usefulness_separate_from_truth": True, "consent_gate": True, "deletion": True, "execution_authority": "none"}, ensure_ascii=False))
