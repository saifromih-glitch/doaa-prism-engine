import json

from doaa_web_source_connector import AllowlistedWebSource, validate_source_url

assert validate_source_url("https://www.mediawiki.org/wiki/API", ["www.mediawiki.org"]) is True
assert validate_source_url("http://www.mediawiki.org/wiki/API", ["www.mediawiki.org"]) is False
assert validate_source_url("https://evil.example/wiki/API", ["www.mediawiki.org"]) is False
assert validate_source_url("https://user:pass@www.mediawiki.org/wiki/API", ["www.mediawiki.org"]) is False
connector = AllowlistedWebSource(["www.mediawiki.org"])
doc = connector.build_document("https://www.mediawiki.org/wiki/API", b"<html><title>API Docs</title><p>Untrusted page data</p></html>")
assert doc["status"] == "source_document_ready"
assert doc["source_title"] == "API Docs"
assert doc["source_data_is_untrusted"] is True
assert doc["automatic_library_update"] is False
assert connector.fetch("https://evil.example/")["reason"] == "source_not_allowlisted"
print(json.dumps({"tests": 7, "status": "passed", "allowlist": True, "https_only": True, "automatic_library_update": False, "execution_authority": "none"}, ensure_ascii=False))
