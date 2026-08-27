import json
import tempfile
from pathlib import Path

from doaa_knowledge_registry import KnowledgeRegistry

candidate = {"record_id": "K-0001", "algorithm_id": "marketing.campaign.v1", "library": "marketing", "version": "1", "evidence_ids": ["E-0001"], "input_schema": {"brief": "string"}, "output_schema": {"claims": "array"}}
registry = KnowledgeRegistry()
proposal = registry.propose(candidate)
assert proposal["status"] == "knowledge_proposal_recorded"
assert proposal["automatic_promotion"] is False
assert registry.resolve("marketing.campaign.v1", "marketing", "1")["status"] == "knowledge_miss"
assert registry.promote("K-0001", "human-reviewer")["status"] == "knowledge_promoted"
resolved = registry.resolve("marketing.campaign.v1", "marketing", "1")
assert resolved["status"] == "knowledge_active_match"
assert resolved["record"]["execution_authority"] == "none"
assert registry.promote("K-0001", "human-reviewer")["reason"] == "record_not_pending"
assert registry.register({"record_id": "K-0002", "algorithm_id": "x", "library": "unknown", "version": "1", "status": "active", "evidence_ids": [], "input_schema": {}, "output_schema": {}})["status"] == "knowledge_operation_blocked"
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "registry.json"
    assert registry.save(path)["status"] == "knowledge_registry_saved"
    loaded = KnowledgeRegistry.load(path)
    assert loaded.list(library="marketing", status="active")["count"] == 1
print(json.dumps({"tests": 8, "status": "passed", "human_promotion_only": True, "automatic_capability_creation": False, "execution_authority": "none"}, ensure_ascii=False))
