import json

from doaa_reuse_ledger import ReuseLedger

ledger = ReuseLedger()
assert ledger.observe("route_local_algorithm", 1000, 300)["event"] == "local_hit"
assert ledger.observe("route_model_or_review")["event"] == "local_miss"
assert ledger.observe("unified_flow_blocked")["event"] == "route_blocked"
stats = ledger.stats()
assert stats["local_hits"] == 1
assert stats["local_misses"] == 1
assert stats["blocked_routes"] == 1
assert stats["hit_rate"] == 0.5
assert stats["token_saving_observed"] == 700
assert stats["selection_policy"] == "exact_local_only"
print(json.dumps({"tests": 7, "status": "passed", "exact_local_only": True, "token_saving_telemetry": True, "execution_authority": "none"}))
