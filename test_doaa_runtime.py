import json

from doaa_algorithm_library import AlgorithmLibrary
from doaa_multi_source_coordinator import MultiSourceCoordinator
from doaa_runtime import DoaaRuntime

request = {"intent": "campaign", "language": "ar"}
message = {"protocol": "doaa.alg.v1", "request_id": "runtime-1", "algorithm": {"id": "marketing.campaign.v1", "version": "1"}, "authority": "none", "automatic_execution": False}
algorithms = AlgorithmLibrary()
assert algorithms.register_validated("marketing.campaign.v1", message, request, "R-1", domain="business", subdomain="marketing")["status"] == "library_entry_registered"
runtime = DoaaRuntime(MultiSourceCoordinator(algorithms))
local = runtime.prepare({"request": request, "library": "marketing", "algorithm_id": "marketing.campaign.v1", "source_request": request})
assert local["status"] == "runtime_ready"
assert local["route"]["status"] == "route_local_algorithm"
assert local["next_action"] == "use_local_payload"
missing = runtime.prepare({"request": {"intent": "new"}, "library": "marketing", "algorithm_id": "new.v1", "source_request": {"intent": "new"}})
assert missing["route"]["status"] == "route_model_or_review"
assert missing["next_action"] == "explicit_adapter_or_human_review"
extra = runtime.prepare({"request": request, "library": "marketing", "unexpected": True})
assert extra["reason"] == "envelope_keys_not_allowed"
invalid = runtime.prepare({"request": request, "library": "unknown"})
assert invalid["status"] == "runtime_blocked" and invalid["route"]["status"] == "unified_flow_blocked"
print(json.dumps({"tests": 8, "status": "passed", "local_first": True, "explicit_adapter_only": True, "execution_authority": "none"}, ensure_ascii=False))
