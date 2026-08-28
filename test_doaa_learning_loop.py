import json

from doaa_feedback import FeedbackStore
from doaa_learning_loop import GovernedLearningLoop

loop = GovernedLearningLoop()
request = {"protocol": "doaa.alg.v1", "capability": "software.task", "slots": {"language": "ar"}}
result = {"protocol": "doaa.alg.v1", "authority": "none", "automatic_execution": False}
message = {"protocol": "doaa.alg.v1", "algorithm": {"id": "software.task.v1", "version": "1"}, "authority": "none", "automatic_execution": False}
metrics = {"baseline_tokens": 1000, "compact_tokens": 300, "quality_score": 0.95, "safety_pass": True}
proposal = loop.observe_and_propose("exp-loop-1", "user-session", "2026-08-28T00:00:00Z", request, result, "user_allowed", "cand-loop-1", "software.task", message, metrics)
assert proposal["status"] == "learning_candidate_ready"
assert proposal["promotion_requires_human"] is True
assert proposal["candidate"]["state"] == "candidate"
assert loop.registry.get_active("software.task")["reason"] == "active_record_not_found"
rejected = loop.observe_and_propose("exp-loop-2", "user-session", "2026-08-28T00:00:00Z", request, result, "user_allowed", "cand-loop-2", "software.task", message, {**metrics, "safety_pass": False})
assert rejected["status"] == "learning_candidate_rejected"
feedback = FeedbackStore()
assert feedback.submit({"feedback_id": "fb-loop-1", "interaction_id": "int-loop-1", "usefulness": 5, "correctness_signal": "believed_true", "consent_to_learning": True, "created_at": "2026-08-28T00:00:00Z"})["status"] == "feedback_recorded"
signal = loop.assess_feedback(feedback, "fb-loop-1", "cand-loop-1")
assert signal["status"] == "feedback_blocks_candidate"
verified_signal = loop.assess_feedback(feedback, "fb-loop-1", "cand-loop-1", "verified_true")
assert verified_signal["status"] == "feedback_supports_candidate"
assert verified_signal["promotion_eligible"] is False
print(json.dumps({"tests": 11, "status": "passed", "automatic_candidate_generation": True, "feedback_integrated": True, "automatic_promotion": False, "execution_authority": "none"}, ensure_ascii=False))
