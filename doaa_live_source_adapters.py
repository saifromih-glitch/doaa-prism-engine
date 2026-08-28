"""Explicit, allowlisted live-source adapters for Doaa evidence review.

Network access exists only when a caller explicitly invokes one of the fetch
methods. Returned data is untrusted and is not inserted into the evidence
store or algorithm libraries automatically.
"""
from __future__ import annotations

import hashlib
import json
import ssl
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

CONTRACT = "doaa.live_sources.v1"
MAX_BYTES = 512_000
TIMEOUT_SECONDS = 10
USER_AGENT = "Doaa-LiveEvidence/0.1 (+https://github.com/saifromih-glitch/doaa-prism-engine)"
_WIKIMEDIA_HOSTS = {"en.wikipedia.org", "ar.wikipedia.org"}
_GITHUB_HOSTS = {"api.github.com"}


class LiveSourceAdapters:
    """Read-only adapters with fixed hosts and path prefixes."""

    def fetch_wikimedia_summary(self, title: Any, language: str = "en") -> dict[str, Any]:
        if not isinstance(title, str) or not title.strip() or len(title) > 256:
            return _blocked("title_invalid")
        if language not in {"en", "ar"}:
            return _blocked("language_not_allowlisted")
        host = f"{language}.wikipedia.org"
        url = f"https://{host}/api/rest_v1/page/summary/{quote(title.strip(), safe='')}"
        result = self._fetch_json(url, _WIKIMEDIA_HOSTS, "/api/rest_v1/page/summary/")
        if result["status"] != "source_document_ready":
            return result
        payload = result["json"]
        if not isinstance(payload, dict):
            return _blocked("source_payload_invalid")
        result["source_title"] = str(payload.get("title") or title)[:512]
        return result

    def search_github_repositories(self, query: Any) -> dict[str, Any]:
        if not isinstance(query, str) or not query.strip() or len(query) > 256:
            return _blocked("query_invalid")
        url = "https://api.github.com/search/repositories?" + urlencode({"q": query.strip()})
        result = self._fetch_json(url, _GITHUB_HOSTS, "/search/repositories")
        if result["status"] != "source_document_ready":
            return result
        payload = result["json"]
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            return _blocked("source_payload_invalid")
        result["source_title"] = f"GitHub repository search: {query.strip()}"[:512]
        return result

    @staticmethod
    def build_evidence_record(document: Any, evidence_id: Any, claim: Any, evidence_span: Any, domain: Any) -> dict[str, Any]:
        if not isinstance(document, dict) or document.get("status") != "source_document_ready":
            return _blocked("source_document_required")
        if not all(isinstance(value, str) and value.strip() for value in (evidence_id, claim, evidence_span, domain)):
            return _blocked("evidence_fields_invalid")
        if domain not in {"science", "industry", "software", "business", "education", "language", "general"}:
            return _blocked("domain_not_allowlisted")
        return {
            "evidence_id": evidence_id,
            "source_url": document["source_url"],
            "source_title": document["source_title"],
            "retrieved_at": document["retrieved_at"],
            "content_digest": document["content_digest"],
            "claim": claim,
            "evidence_span": evidence_span,
            "domain": domain,
            "status": "pending_review",
            "source_data_is_untrusted": True,
            "automatic_library_update": False,
            "execution_authority": "none",
            "automatic_execution": False,
        }

    @staticmethod
    def _fetch_json(url: str, allowed_hosts: set[str], path_prefix: str) -> dict[str, Any]:
        if not _allowlisted_url(url, allowed_hosts, path_prefix):
            return _blocked("source_not_allowlisted")
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, method="GET")
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS, context=ssl.create_default_context()) as response:
                final_url = response.geturl()
                if not _allowlisted_url(final_url, allowed_hosts, path_prefix):
                    return _blocked("redirect_target_not_allowlisted")
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    return _blocked("source_size_exceeded")
                content_type = response.headers.get_content_type()
                if content_type != "application/json":
                    return _blocked("content_type_not_supported")
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return _blocked("source_fetch_failed")
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return {
            "status": "source_document_ready",
            "contract": CONTRACT,
            "source_url": final_url,
            "source_title": final_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "content_digest": hashlib.sha256(body).hexdigest(),
            "content": canonical,
            "json": payload,
            "source_data_is_untrusted": True,
            "automatic_evidence_approval": False,
            "automatic_library_update": False,
            "execution_authority": "none",
            "automatic_execution": False,
        }


def _allowlisted_url(url: Any, hosts: set[str], path_prefix: str) -> bool:
    parsed = urlparse(url) if isinstance(url, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.hostname in hosts and not parsed.username and not parsed.password and parsed.path.startswith(path_prefix) and len(url) <= 2048)


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "source_fetch_blocked", "contract": CONTRACT, "reason": reason, "source_data_is_untrusted": True, "automatic_evidence_approval": False, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}
