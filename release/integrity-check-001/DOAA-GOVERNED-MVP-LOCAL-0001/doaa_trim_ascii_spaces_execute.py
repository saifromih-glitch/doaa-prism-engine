import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(value):
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def blocked(reason):
    return {
        "status": "trim_ascii_spaces_blocked",
        "reason": reason,
        "execution_started": False,
        "source_modified": False,
        "model_execution_authority": "none",
        "network_request": False,
    }


def execute(payload):
    proposal = payload.get("proposal", {})
    review = payload.get("human_review", {})
    inp = Path(payload.get("input_path", "")).resolve()
    out = Path(payload.get("output_path", "")).resolve()
    root = Path(payload.get("allowed_root", "")).resolve()
    if inp.suffix.lower() != ".csv" or not inp.is_file():
        return blocked("csv_input_required")
    if not root.is_dir() or root not in out.parents or out.exists() or inp == out:
        return blocked("output_policy_violation")
    if (proposal.get("operation") != "trim_ascii_spaces"
            or proposal.get("arguments") != {}
            or not isinstance(proposal.get("column"), str)
            or not proposal.get("column")):
        return blocked("proposal_not_allowed")
    if (proposal.get("execution_authority") != "none"
            or review.get("status") != "accepted_by_human"
            or review.get("execution_authority") != "none"):
        return blocked("human_acceptance_required")
    if review.get("proposal_sha256") != sha(canon(proposal)):
        return blocked("proposal_hash_mismatch")
    if not isinstance(review.get("audit_record_sha256"), str) or len(review["audit_record_sha256"]) != 64:
        return blocked("audit_hash_required")
    with inp.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if proposal["column"] not in fields:
            return blocked("target_column_missing")
        rows = list(reader)
    before = [dict(row) for row in rows]
    changed = 0
    for row in rows:
        old = row[proposal["column"]]
        if not isinstance(old, str):
            return blocked("target_cell_not_text")
        new = old.strip(" ")
        if new != old:
            changed += 1
        row[proposal["column"]] = new
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    non_target = [
        name for name in fields if name != proposal["column"]
        and any(before[i][name] != rows[i][name] for i in range(len(rows)))
    ]
    if len(rows) != len(before) or fields != (reader.fieldnames or []) or non_target:
        out.unlink(missing_ok=True)
        return blocked("invariant_failure")
    return {
        "status": "trim_ascii_spaces_executed_safe_file",
        "operation": proposal["operation"],
        "target_column": proposal["column"],
        "changed_cell_count": changed,
        "row_count_before": len(before),
        "row_count_after": len(rows),
        "columns_before": fields,
        "columns_after": fields,
        "non_target_columns_changed": non_target,
        "input_sha256": sha(inp.read_bytes()),
        "output_sha256": sha(out.read_bytes()),
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_modified": False,
        "model_execution_authority": "none",
        "network_request": False,
        "execution_started": True,
        "output_path": str(out),
    }


def main():
    print(json.dumps(execute(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
