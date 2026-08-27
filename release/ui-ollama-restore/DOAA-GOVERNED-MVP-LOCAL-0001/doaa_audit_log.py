import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


AUDIT_SCHEMA = "DOAA-AUDIT-0001"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_record(request, raw_model_text, repaired_model_text, gate_result, repair_id=None, previous_hash=None):
    raw = raw_model_text if isinstance(raw_model_text, str) else ""
    repaired = repaired_model_text if isinstance(repaired_model_text, str) else ""
    record = {
        "schema": AUDIT_SCHEMA,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "contract_id": "CONTRACT-LLM-0003-BOUNDED-PROPOSAL-REPAIR",
        "request_sha256": sha256_text(canonical(request)),
        "raw_response_sha256": sha256_text(raw),
        "repaired_response_sha256": sha256_text(repaired),
        "proposal_sha256": sha256_text(canonical(gate_result.get("proposal", {}))) if isinstance(gate_result, dict) else None,
        "repair_id": repair_id,
        "gate_status": gate_result.get("status"),
        "gate_reason": gate_result.get("reason"),
        "execution_authority": "none",
        "dsl_execution": False,
        "external_network_request": False,
        "raw_preserved": True,
        "previous_record_sha256": previous_hash,
    }
    record["record_sha256"] = sha256_text(canonical(record))
    return record


def append_record(path, record):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(record) + "\n")


def main():
    payload = json.loads(sys.stdin.read())
    record = make_record(
        payload.get("request"),
        payload.get("raw_model_text"),
        payload.get("repaired_model_text"),
        payload.get("gate_result", {}),
        payload.get("repair_id"),
        payload.get("previous_record_sha256"),
    )
    append_record(payload["audit_path"], record)
    sys.stdout.write(canonical(record))


if __name__ == "__main__":
    main()
