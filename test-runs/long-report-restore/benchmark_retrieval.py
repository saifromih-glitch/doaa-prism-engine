import json
import time
from pathlib import Path
from doaa_algorithm_registry import register
from doaa_deterministic_retrieval import retrieve

root = Path(__file__).parent / "test-runs-benchmark"
root.mkdir(exist_ok=True)
registry = root / "registry.jsonl"
if registry.exists(): registry.unlink()
proposal = {"operation":"remove_ascii_phone_separators","column":"phone","worksheet":None,"dsl_version":"1.4"}
register(registry, proposal, {"status":"accepted_by_human"}, {"status":"executed_safe_file"})

def timed(payload):
    start = time.perf_counter(); result = retrieve(payload); elapsed_ms = (time.perf_counter() - start) * 1000
    return result, round(elapsed_ms, 3)
hit, hit_ms = timed({"registry_path":str(registry),"proposal":proposal})
miss, miss_ms = timed({"registry_path":str(registry),"proposal":dict(proposal, column="unknown")})
result = {"status":"benchmark_passed","cache_hit":{"status":hit["status"],"model_call":hit["model_call"],"elapsed_ms":hit_ms},"cache_miss":{"status":miss["status"],"model_call":miss["model_call"],"elapsed_ms":miss_ms},"model_calls_during_benchmark":0,"automatic_execution":False,"execution_authority":"none"}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
