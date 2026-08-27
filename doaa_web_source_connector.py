"""Explicit allowlisted fetcher for web evidence.

This connector is outside Doaa's core. It fetches source data only; it does
not interpret page instructions, call a model, store records, or update a
library automatically.
"""
from __future__ import annotations

import hashlib
import ssl
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_BYTES = 512_000
USER_AGENT = "Doaa-WebEvidence/0.1 (+https://github.com/saifromih-glitch/doaa-prism-engine)"


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.in_title = tag.lower() == "title"

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data.strip())


def validate_source_url(url: Any, allowed_hosts: Iterable[str]) -> bool:
    parsed = urlparse(url) if isinstance(url, str) else None
    hosts = {h.lower().strip() for h in allowed_hosts}
    return bool(parsed and parsed.scheme == "https" and parsed.hostname and parsed.hostname.lower() in hosts and not parsed.username and not parsed.password and len(url) <= 2048)


class AllowlistedWebSource:
    def __init__(self, allowed_hosts: Iterable[str], max_bytes: int = MAX_BYTES) -> None:
        self.allowed_hosts = {h.lower().strip() for h in allowed_hosts}
        self.max_bytes = max(1024, min(max_bytes, MAX_BYTES))

    def fetch(self, url: Any) -> dict[str, Any]:
        if not validate_source_url(url, self.allowed_hosts):
            return self._blocked("source_not_allowlisted")
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain;q=0.9"}, method="GET")
        try:
            with urlopen(request, timeout=10, context=ssl.create_default_context()) as response:
                final_url = response.geturl()
                if not validate_source_url(final_url, self.allowed_hosts):
                    return self._blocked("redirect_target_not_allowlisted")
                body = response.read(self.max_bytes + 1)
                if len(body) > self.max_bytes:
                    return self._blocked("source_size_exceeded")
                content_type = response.headers.get_content_type()
                if content_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
                    return self._blocked("content_type_not_supported")
                return self.build_document(final_url, body, content_type)
        except Exception:
            return self._blocked("source_fetch_failed")

    @staticmethod
    def build_document(url: str, body: bytes, content_type: str = "text/html") -> dict[str, Any]:
        text = body.decode("utf-8", errors="replace")
        parser = _TitleParser()
        if "html" in content_type:
            parser.feed(text)
        title = " ".join("".join(parser.parts).split())[:512] or url
        return {"status": "source_document_ready", "source_url": url, "source_title": title, "retrieved_at": datetime.now(timezone.utc).isoformat(), "content_digest": hashlib.sha256(body).hexdigest(), "content": text, "source_data_is_untrusted": True, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {"status": "source_fetch_blocked", "reason": reason, "automatic_library_update": False, "execution_authority": "none", "automatic_execution": False}
