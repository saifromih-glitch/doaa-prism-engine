import json

from doaa_confidence import score_signals

unknown = score_signals(5, "believed_true", True, 1000, 300)
assert unknown["status"] == "confidence_signals_ready"
assert unknown["usefulness_score"] == 1.0
assert unknown["correctness_score"] is None
assert unknown["truth_claim"] == "not_established"
assert unknown["quality_for_promotion"] is True
verified = score_signals(4, "believed_true", True, 1000, 300, "verified_true")
assert verified["correctness_score"] == 1.0
assert verified["correctness_is_verified"] is True
assert verified["truth_claim"] == "supported_by_evidence"
false = score_signals(5, "believed_true", True, 1000, 300, "verified_false")
assert false["correctness_score"] == 0.0
assert false["quality_for_promotion"] is False
assert false["truth_claim"] == "contradicted"
assert score_signals(5, "unknown", False, 1000, 300)["quality_for_promotion"] is False
assert score_signals(5, "unknown", True, 1000, 1200)["quality_for_promotion"] is False
assert score_signals(6, "unknown", True, 1000, 300)["status"] == "confidence_blocked"
assert score_signals(5, "unknown", True, 0, 0)["status"] == "confidence_blocked"
print(json.dumps({"tests": 9, "status": "passed", "truth_separated": True, "safety_dimension": True, "token_dimension": True, "execution_authority": "none"}, ensure_ascii=False))
