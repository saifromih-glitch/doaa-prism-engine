import csv
import hashlib
import json
import sys
from pathlib import Path


ALLOWED_ROOT_NAME = "test-runs"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def blocked(reason):
    return {"status":"execution_blocked","reason":reason,"execution_started":False,"execution_authority":"none","source_modified":False}


def safe_path(path_text, root):
    path = Path(path_text).resolve()
    root = Path(root).resolve()
    return path == root or root in path.parents


def execute(payload):
    proposal = payload.get("proposal")
    review = payload.get("human_review")
    input_path = Path(payload.get("input_path", ""))
    output_path = Path(payload.get("output_path", ""))
    allowed_root = Path(payload.get("allowed_root", ""))
    if payload.get("mode") != "explicit_test":
        return blocked("explicit_test_mode_required")
    if not isinstance(proposal, dict) or proposal.get("operation") != "remove_ascii_phone_separators" or proposal.get("column") != "phone" or proposal.get("arguments") != {}:
        return blocked("proposal_not_allowed")
    if not isinstance(review, dict) or review.get("status") != "accepted_by_human":
        return blocked("human_acceptance_required")
    if review.get("execution_authority") != "none" or proposal.get("execution_authority") != "none":
        return blocked("authority_invalid")
    if allowed_root.name != ALLOWED_ROOT_NAME or not safe_path(input_path, allowed_root) or not safe_path(output_path, allowed_root):
        return blocked("path_outside_test_root")
    if input_path == output_path or not input_path.is_file():
        return blocked("input_output_path_invalid")
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if "phone" not in fieldnames:
            return blocked("target_column_missing")
        rows = list(reader)
    before = [dict(row) for row in rows]
    after = [dict(row) for row in rows]
    changed = 0
    for row_before, row_after in zip(before, after):
        original = row_before["phone"]
        transformed = original.replace(" ", "").replace("-", "")
        row_after["phone"] = transformed
        changed += transformed != original
    for row_before, row_after in zip(before, after):
        for key in fieldnames:
            if key != "phone" and row_before[key] != row_after[key]:
                return blocked("non_target_column_changed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(after)
    receipt = {
        "status":"executed_test_only",
        "mode":"explicit_test",
        "input_sha256":sha256(canonical(before)),
        "output_sha256":sha256(canonical(after)),
        "changed_cell_count":changed,
        "row_count_before":len(before),
        "row_count_after":len(after),
        "columns_before":fieldnames,
        "columns_after":fieldnames,
        "non_target_columns_unchanged":True,
        "execution_started":True,
        "execution_authority":"none",
        "source_modified":False,
        "external_network_request":False,
        "output_path":str(output_path),
    }
    return receipt


def main():
    print(canonical(execute(json.loads(sys.stdin.read()))))


if __name__ == "__main__":
    main()
