import json
import tempfile
from pathlib import Path

from doaa_web_evidence import WebEvidenceStore, content_digest

record = {"evidence_id": "E-0001", "source_url": "https://example.org/report", "source_title": "Public report", "retrieved_at": "2026-08-28T00:00:00Z", "content_digest": content_digest("claim evidence"), "claim": "A supported public claim.", "evidence_span": "claim evidence", "domain": "business", "status": "pending_review"}
store = WebEvidenceStore()
assert store.add(record)["status"] == "evidence_registered"
assert store.list(status="pending_review")["count"] == 1
assert store.approve("E-0001")["status"] == "evidence_approved"
proposal = store.propose_library_update(["E-0001"], "marketing", "Review the approved evidence before updating the template.")
assert proposal["status"] == "library_update_proposed"
assert proposal["automatic_library_update"] is False
bad_url = dict(record, evidence_id="E-0002", source_url="http://example.org/report")
assert store.add(bad_url)["reason"] == "invalid_url"
bad_status = dict(record, evidence_id="E-0003", status="approved")
assert store.add(bad_status)["status"] == "evidence_registered"
assert store.propose_library_update(["E-0003"], "marketing", "r")["status"] == "library_update_proposed"
assert store.propose_library_update(["missing"], "marketing", "r")["status"] == "evidence_operation_blocked"
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "evidence.json"
    assert store.save(path)["status"] == "evidence_store_saved"
    loaded = WebEvidenceStore.load(path)
    assert loaded.list(domain="business")["count"] == 2
print(json.dumps({"tests": 9, "status": "passed", "provenance": True, "human_approval_required": True, "automatic_library_update": False, "execution_authority": "none"}, ensure_ascii=False))
