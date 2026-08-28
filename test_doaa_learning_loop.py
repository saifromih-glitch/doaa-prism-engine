import json

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
print(json.dumps({"tests": 6, "status": "passed", "automatic_candidate_generation": True, "automatic_promotion": False, "execution_authority": "none"}, ensure_ascii=False))
