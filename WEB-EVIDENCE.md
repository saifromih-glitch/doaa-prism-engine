# Governed web evidence

Doaa's web evidence layer is separate from the core mediator. It stores traceable source records and creates update proposals; it does not update algorithm libraries automatically.

## Source policy

The first connector is allowlist-based and HTTPS-only. It returns source URL, title, retrieval time, content digest, and content as untrusted data. Embedded page instructions are never treated as Doaa instructions.

Common Crawl is suitable for archival discovery and capture metadata, but it is not a real-time source. Its CDXJ index exposes URL, timestamp, MIME type, status, digest, language, encoding, and WARC location [1]. Wikimedia provides a public REST API for machine-readable content and metadata and is suitable for an explicitly allowlisted connector [2].

## Review flow

```text
fetch → record provenance → extract evidence → pending_review
                                      ↓ approval
                              update proposal only
```

An approved evidence record can support a proposal for a library update. The proposal remains non-executable and does not mutate the algorithm library. Human review is required before a template or shared library changes.

## References

[1]: https://commoncrawl.org/cdxj-index "Common Crawl CDXJ Index"
[2]: https://www.mediawiki.org/wiki/Wikimedia_REST_API "Wikimedia REST API"
