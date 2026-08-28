import json

from doaa_algorithm_library import AlgorithmLibrary
from doaa_multi_source_coordinator import MultiSourceCoordinator
from doaa_runtime import DoaaRuntime
from doaa_template_reconstruction import TemplateRegistry

registry = TemplateRegistry()
slots = {"goal": "إطلاق منتج جديد", "audience": "مطورو برمجيات", "channel": "web", "language": "ar"}
rebuilt = registry.reconstruct("marketing.campaign.v1", slots)
assert rebuilt["status"] == "reconstruction_ready"
assert rebuilt["request"]["capability"] == "marketing.campaign"
assert rebuilt["request"]["slots"]["goal"] == "إطلاق منتج جديد"
assert rebuilt["slot_order"] == ["goal", "audience", "channel", "language"]
assert rebuilt["message"]["authority"] == "none"
assert rebuilt["message"]["automatic_execution"] is False
assert registry.reconstruct("marketing.campaign.v1", {**slots, "extra": "x"})["reason"] == "unknown_slot"
assert registry.reconstruct("marketing.campaign.v1", {"goal": "x"})["reason"] == "missing_required_slot"
assert registry.reconstruct("marketing.campaign.v1", {**slots, "goal": ""})["reason"] == "slot_value_invalid"
assert registry.reconstruct("unknown.template.v1", slots)["status"] == "governed_capability_request"

algorithms = AlgorithmLibrary()
request = rebuilt["request"]
message = rebuilt["message"]
assert algorithms.register_validated("marketing.campaign.v1", message, request, "rebuild-1", domain="business", subdomain="marketing")["status"] == "library_entry_registered"
runtime = DoaaRuntime(MultiSourceCoordinator(algorithms))
result = runtime.prepare_reconstruction("marketing.campaign.v1", slots)
assert result["status"] == "runtime_ready"
assert result["route"]["status"] == "route_local_algorithm"
assert result["next_action"] == "use_local_payload"
blocked = runtime.prepare_reconstruction("marketing.campaign.v1", {"goal": "x"})
assert blocked["status"] == "runtime_blocked"
print(json.dumps({"tests": 13, "status": "passed", "template_exact": True, "arabic_utf8": True, "local_reuse": True, "execution_authority": "none"}, ensure_ascii=False))
