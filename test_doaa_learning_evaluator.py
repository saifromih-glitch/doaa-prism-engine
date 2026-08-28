import json

from doaa_learning_evaluator import evaluate_candidate

passed = evaluate_candidate({"baseline_tokens": 1000, "compact_tokens": 300, "quality_score": 0.95, "safety_pass": True})
assert passed["status"] == "passed"
assert passed["promotion_eligible"] is True
assert passed["token_saving"] == 700
assert passed["token_saving_ratio"] == 0.7
assert evaluate_candidate({"baseline_tokens": 1000, "compact_tokens": 300, "quality_score": 0.89, "safety_pass": True})["status"] == "failed"
assert evaluate_candidate({"baseline_tokens": 1000, "compact_tokens": 300, "quality_score": 0.95, "safety_pass": False})["status"] == "failed"
assert evaluate_candidate({"baseline_tokens": 1000, "compact_tokens": 1200, "quality_score": 0.99, "safety_pass": True})["status"] == "failed"
assert evaluate_candidate({"baseline_tokens": 0, "compact_tokens": 0, "quality_score": 1, "safety_pass": True})["status"] == "evaluation_blocked"
assert evaluate_candidate({"baseline_tokens": 1000, "compact_tokens": 300, "quality_score": 0.95, "safety_pass": "yes"})["status"] == "evaluation_blocked"
print(json.dumps({"tests": 7, "status": "passed", "token_saving_gate": True, "quality_gate": True, "safety_gate": True, "execution_authority": "none"}))
