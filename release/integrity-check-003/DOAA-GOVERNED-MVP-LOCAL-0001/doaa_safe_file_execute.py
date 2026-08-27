import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def blocked(reason):
    return {"status":"execution_blocked","reason":reason,"execution_started":False,"model_execution_authority":"none","source_modified":False,"network_request":False}


def under(path, root):
    return path == root or root in path.parents


def execute(payload):
    proposal = payload.get("proposal")
    review = payload.get("human_review")
    input_path = Path(payload.get("input_path", "")).resolve()
    output_path = Path(payload.get("output_path", "")).resolve()
    allowed_root = Path(payload.get("allowed_root", "")).resolve()
    if not isinstance(proposal, dict) or proposal.get("kind") != "proposal":
        return blocked("proposal_invalid")
    if proposal.get("operation") != "remove_ascii_phone_separators" or proposal.get("column") != "phone" or proposal.get("arguments") != {}:
        return blocked("proposal_not_allowed")
    if not isinstance(review, dict) or review.get("status") != "accepted_by_human":
        return blocked("human_acceptance_required")
    if review.get("execution_authority") != "none" or proposal.get("execution_authority") != "none":
        return blocked("authority_invalid")
    if review.get("proposal_sha256") != sha256(canonical(proposal)):
        return blocked("proposal_hash_mismatch")
    if not isinstance(review.get("audit_record_sha256"), str) or len(review["audit_record_sha256"]) != 64:
        return blocked("audit_hash_required")
    if not allowed_root.is_dir() or not under(output_path, allowed_root):
        return blocked("output_outside_allowed_root")
    if input_path.suffix.lower() != ".csv" or input_path == output_path or not input_path.is_file() or output_path.exists():
        return blocked("input_output_policy_violation")
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if "phone" not in fieldnames:
            return blocked("target_column_missing")
        before = [dict(row) for row in reader]
    after = [dict(row) for row in before]
    changed = 0
    for old, new in zip(before, after):
        if not isinstance(old["phone"], str):
            return blocked("target_cell_not_text")
        new["phone"] = old["phone"].replace(" ", "").replace("-", "")
        changed += new["phone"] != old["phone"]
    invariants = {
        "row_count_unchanged": len(before) == len(after),
        "column_set_unchanged": fieldnames == list(after[0].keys()) if after else True,
        "non_target_columns_unchanged": all(
            all(old[key] == new[key] for key in fieldnames if key != "phone")
            for old, new in zip(before, after)
        ),
        "only_ascii_spaces_and_hyphens_removed": all(
            new["phone"] == old["phone"].replace(" ", "").replace("-", "")
            for old, new in zip(before, after)
        ),
    }
    if not all(invariants.values()):
        return blocked("invariant_failure")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(after)
    return {
        "status":"executed_safe_file",
        "execution_timestamp_utc":datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input_sha256":sha256(canonical(before)),
        "output_sha256":sha256(canonical(after)),
        "row_count_before":len(before),
        "row_count_after":len(after),
        "columns_before":fieldnames,
        "columns_after":fieldnames,
        "changed_cell_count":changed,
        "comparison_result":"passed",
        "invariants":invariants,
        "output_path":str(output_path),
        "execution_started":True,
        "model_execution_authority":"none",
        "source_modified":False,
        "network_request":False,
    }


def main():
    print(canonical(execute(json.loads(sys.stdin.read()))))


if __name__ == "__main__":
    main()
