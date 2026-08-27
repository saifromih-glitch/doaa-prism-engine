import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import doaa_algorithm_registry as registry
import doaa_premodel_router as router

with tempfile.TemporaryDirectory() as t:
    path = Path(t) / "registry.jsonl"
    proposal = {"operation": "normalize_ascii_spaces", "column": "name", "worksheet": None, "dsl_version": "1.4"}
    registered = registry.register(path, proposal, {"status": "accepted_by_human"}, {"status": "space_normalize_executed_safe_file"})
    assert registered["status"] == "registered"
    hit = router.route({"registry_path": str(path), "proposal": proposal})
    assert hit["route"] == "reuse_candidate"
    assert hit["model_call"] is False
    assert hit["automatic_execution"] is False
    assert hit["execution_authority"] == "none"
    miss = router.route({"registry_path": str(path), "proposal": {"operation": "unknown", "column": "name", "worksheet": None, "dsl_version": "1.4"}})
    assert miss["route"] == "governed_model_stage"
    assert miss["model_call"] is True
    assert miss["automatic_execution"] is False
    assert miss["execution_authority"] == "none"
    assert "execution_started" not in miss or miss.get("execution_started") is False
print(json.dumps({"tests":8,"status":"passed","cache_hit_model_call":False,"cache_miss_non_executable":True,"execution_authority":"none"}, ensure_ascii=False))
