import hashlib
import json
import re
import sys
from datetime import datetime, timezone

URL = re.compile(r"^https?://[^\s]{1,2048}$")


def gate(record):
    if not isinstance(record, dict) or set(record) != {"source_url", "title", "excerpt"}:
        return {"status":"web_research_blocked","reason":"source_schema_invalid","execution_authority":"none","automatic_execution":False}
    if not isinstance(record["source_url"], str) or not URL.fullmatch(record["source_url"]):
        return {"status":"web_research_blocked","reason":"public_http_url_required","execution_authority":"none","automatic_execution":False}
    if not isinstance(record["title"], str) or not 1 <= len(record["title"]) <= 512:
        return {"status":"web_research_blocked","reason":"title_invalid","execution_authority":"none","automatic_execution":False}
    if not isinstance(record["excerpt"], str) or not 1 <= len(record["excerpt"]) <= 10000:
        return {"status":"web_research_blocked","reason":"excerpt_invalid","execution_authority":"none","automatic_execution":False}
    source_hash = hashlib.sha256(record["excerpt"].encode("utf-8")).hexdigest()
    return {"status":"web_source_accepted_read_only","source_url":record["source_url"],"title":record["title"],"retrieved_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"source_hash":source_hash,"execution_authority":"none","automatic_execution":False,"execution_started":False,"result_to_execution":"forbidden_without_separate_validation"}


def main():
    print(json.dumps(gate(json.loads(sys.stdin.read())),ensure_ascii=False,sort_keys=True,separators=(",",":")))

if __name__ == "__main__": main()
