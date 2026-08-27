import json

from doaa_algorithm_library import AlgorithmLibrary
from doaa_knowledge_registry import KnowledgeRegistry
from doaa_multi_source_coordinator import MultiSourceCoordinator
from doaa_web_evidence import WebEvidenceStore, content_digest

request = {"intent": "campaign", "language": "ar"}
message = {"protocol": "doaa.alg.v1", "request_id": "coord-1", "algorithm": {"id": "marketing.campaign.v1", "version": "1"}, "authority": "none", "automatic_execution": False}
algorithms = AlgorithmLibrary()
algorithms.register_validated("marketing.campaign.v1", message, request, "M-0001", domain="business", subdomain="marketing")
coordinator = MultiSourceCoordinator(algorithms)
local = coordinator.prepare(request, "marketing", "marketing.campaign.v1", request)
assert local["status"] == "route_local_algorithm"
assert local["source"] == "algorithm_library"
assert local["execution_authority"] == "none"
unknown = coordinator.prepare({"intent": "new"}, "marketing", "new.v1", {"intent": "new"})
assert unknown["status"] == "route_model_or_review"
assert unknown["requires_explicit_adapter"] is True
fresh = coordinator.prepare(request, "marketing", "none", request, require_fresh_evidence=True)
assert fresh["status"] == "unified_flow_blocked"
assert fresh["reason"] == "fresh_evidence_required"
evidence = WebEvidenceStore()
record = {"evidence_id": "E-1", "source_url": "https://example.org/current", "source_title": "Current source", "retrieved_at": "2026-08-28T00:00:00Z", "content_digest": content_digest("current"), "claim": "Current claim", "evidence_span": "current", "domain": "business", "status": "pending_review"}
assert evidence.add(record)["status"] == "evidence_registered"
assert evidence.approve("E-1")["status"] == "evidence_approved"
coordinator = MultiSourceCoordinator(algorithms, evidence=evidence)
ready = coordinator.prepare({"intent": "fresh"}, "marketing", "fresh.v1", {"intent": "fresh"}, require_fresh_evidence=True, evidence_ids=["E-1"])
assert ready["status"] == "route_model_or_review"
invalid = coordinator.prepare({}, "unknown")
assert invalid["reason"] == "unknown_library"
print(json.dumps({"tests": 9, "status": "passed", "exact_first": True, "freshness_gate": True, "model_explicit_only": True, "execution_authority": "none"}, ensure_ascii=False))
