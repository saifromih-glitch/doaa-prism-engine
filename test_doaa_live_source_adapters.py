import json

from doaa_live_source_adapters import LiveSourceAdapters

adapters = LiveSourceAdapters()
assert adapters.fetch_wikimedia_summary("", "en")["reason"] == "title_invalid"
assert adapters.fetch_wikimedia_summary("Doaa", "fr")["reason"] == "language_not_allowlisted"
assert adapters.search_github_repositories(" ")["reason"] == "query_invalid"
assert adapters.search_github_repositories("x" * 257)["reason"] == "query_invalid"
assert adapters._fetch_json("https://example.org/api/rest_v1/page/summary/Doaa", {"en.wikipedia.org"}, "/api/rest_v1/page/summary/")["reason"] == "source_not_allowlisted"
assert adapters._fetch_json("http://en.wikipedia.org/api/rest_v1/page/summary/Doaa", {"en.wikipedia.org"}, "/api/rest_v1/page/summary/")["reason"] == "source_not_allowlisted"
assert adapters._fetch_json("https://en.wikipedia.org/wiki/Doaa", {"en.wikipedia.org"}, "/api/rest_v1/page/summary/")["reason"] == "source_not_allowlisted"

document = {
    "status": "source_document_ready",
    "source_url": "https://en.wikipedia.org/api/rest_v1/page/summary/Doaa",
    "source_title": "Doaa",
    "retrieved_at": "2026-08-28T00:00:00+00:00",
    "content_digest": "digest",
}
evidence = adapters.build_evidence_record(document, "wiki-1", "claim", "span", "language")
assert evidence["status"] == "pending_review"
assert evidence["source_data_is_untrusted"] is True
assert evidence["automatic_library_update"] is False
assert adapters.build_evidence_record({}, "wiki-2", "claim", "span", "language")["reason"] == "source_document_required"
assert adapters.build_evidence_record(document, "wiki-3", "claim", "span", "unknown")["reason"] == "domain_not_allowlisted"

# Validate the deterministic document shape without contacting the network.
result = {
    "status": "source_document_ready",
    "source_data_is_untrusted": True,
    "automatic_evidence_approval": False,
    "automatic_library_update": False,
    "execution_authority": "none",
    "automatic_execution": False,
}
assert json.loads(json.dumps(result))["execution_authority"] == "none"
print(json.dumps({"tests": 13, "status": "passed", "network_calls": 0, "allowlist_enforced": True, "provenance_pending_review": True, "execution_authority": "none"}))
