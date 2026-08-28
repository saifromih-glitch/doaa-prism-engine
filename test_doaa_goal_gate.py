import json

from doaa_goal_gate import assess_optimization

passed = assess_optimization({"baseline_tokens": 1000, "doaa_tokens": 300, "baseline_quality": 0.90, "doaa_quality": 0.90, "baseline_safety": True, "doaa_safety": True, "sample_count": 20})
assert passed["status"] == "goal_gate_passed"
assert passed["token_saving_ratio"] == 0.7
assert passed["quality_delta"] == 0.0
assert passed["safety_preserved"] is True
better = assess_optimization({"baseline_tokens": 1000, "doaa_tokens": 500, "baseline_quality": 0.80, "doaa_quality": 0.85, "baseline_safety": True, "doaa_safety": True, "sample_count": 1})
assert better["status"] == "goal_gate_passed"
assert assess_optimization({"baseline_tokens": 1000, "doaa_tokens": 300, "baseline_quality": 0.90, "doaa_quality": 0.89, "baseline_safety": True, "doaa_safety": True, "sample_count": 20})["status"] == "goal_gate_failed"
assert assess_optimization({"baseline_tokens": 1000, "doaa_tokens": 300, "baseline_quality": 0.90, "doaa_quality": 0.90, "baseline_safety": True, "doaa_safety": False, "sample_count": 20})["status"] == "goal_gate_failed"
assert assess_optimization({"baseline_tokens": 1000, "doaa_tokens": 1200, "baseline_quality": 0.90, "doaa_quality": 0.95, "baseline_safety": True, "doaa_safety": True, "sample_count": 20})["status"] == "goal_gate_failed"
assert assess_optimization({"baseline_tokens": 0, "doaa_tokens": 0, "baseline_quality": 1, "doaa_quality": 1, "baseline_safety": True, "doaa_safety": True, "sample_count": 1})["status"] == "goal_gate_blocked"
assert assess_optimization({"baseline_tokens": 1000, "doaa_tokens": 300, "baseline_quality": 0.9, "doaa_quality": 0.9, "baseline_safety": True, "doaa_safety": True, "sample_count": 0})["status"] == "goal_gate_blocked"
print(json.dumps({"tests": 7, "status": "passed", "token_reduction_required": True, "quality_regression_blocked": True, "safety_regression_blocked": True, "execution_authority": "none"}, ensure_ascii=False))
