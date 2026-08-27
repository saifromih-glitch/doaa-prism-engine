import json
import tempfile
from pathlib import Path

from doaa_algorithm_library import AlgorithmLibrary, request_fingerprint

request = {"intent": "summarize", "language": "ar", "constraints": {"faithful": True}}
message = {"protocol": "doaa.alg.v1", "request_id": "lib-1", "algorithm": {"id": "answer.summarize.v1", "version": "1"}, "authority": "none", "automatic_execution": False}

library = AlgorithmLibrary()
registered = library.register_validated("answer.summarize.v1", message, request, "R-0001")
assert registered["status"] == "library_entry_registered"
match = library.find_exact("answer.summarize.v1", request)
assert match["status"] == "library_match_found"
assert match["match_type"] == "exact"
miss = library.find_exact("answer.compose.v1", request)
assert miss["status"] == "library_miss"
blocked = library.register({"entry_id": "bad", "algorithm_id": "x", "protocol": "doaa.alg.v1", "message": message, "source_request_fingerprint": request_fingerprint(request), "validation_status": "unvalidated", "authority": "none", "automatic_execution": False})
assert blocked["status"] == "library_operation_blocked"
invalid = library.register_validated("answer.summarize.v1", message, request, "R-0001")
assert invalid["status"] == "library_operation_blocked"
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "library.json"
    assert library.save(path)["status"] == "library_saved"
    loaded = AlgorithmLibrary.load(path)
    assert loaded.find_exact("answer.summarize.v1", request)["status"] == "library_match_found"
print(json.dumps({"tests": 8, "status": "passed", "exact_only": True, "automatic_capability_creation": False, "execution_authority": "none"}, ensure_ascii=False))
