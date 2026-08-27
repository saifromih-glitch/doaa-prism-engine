import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_source(source, registry_path):
    if not isinstance(source, dict) or set(source) != {"source_url", "title", "excerpt", "source_hash"}:
        return {"status":"source_record_blocked","reason":"source_schema_invalid","execution_authority":"none"}
    if not all(isinstance(source[k], str) and source[k] for k in source):
        return {"status":"source_record_blocked","reason":"source_fields_invalid","execution_authority":"none"}
    expected = hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest()
    if source["source_hash"] != expected:
        return {"status":"source_record_blocked","reason":"source_hash_mismatch","execution_authority":"none"}
    entry = {"source_url":source["source_url"],"title":source["title"],"excerpt":source["excerpt"],"source_hash":source["source_hash"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    path = Path(registry_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(entry) + "\n")
    return {"status":"source_recorded_append_only","source_hash":source["source_hash"],"registry_path":str(path),"execution_authority":"none","automatic_execution":False,"source_modified":False}


def main():
    payload=json.loads(input())
    print(json.dumps(record_source(payload["source"],payload["registry_path"]),ensure_ascii=False,sort_keys=True,separators=(",",":")))

if __name__ == "__main__": main()
