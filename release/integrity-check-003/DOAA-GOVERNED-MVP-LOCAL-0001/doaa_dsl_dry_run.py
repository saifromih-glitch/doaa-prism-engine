import hashlib
import json
import sys


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def rejected(reason):
    return {"status":"dry_run_blocked","reason":reason,"execution_started":False,"execution_authority":"none","source_modified":False}


def run(payload):
    proposal = payload.get("proposal")
    review = payload.get("human_review")
    rows = payload.get("rows")
    if not isinstance(proposal, dict) or proposal.get("kind") != "proposal":
        return rejected("proposal_required")
    if not isinstance(review, dict) or review.get("status") != "accepted_by_human":
        return rejected("human_acceptance_required")
    if proposal.get("execution_authority") != "none" or review.get("execution_authority") != "none":
        return rejected("authority_invalid")
    if proposal.get("operation") != "remove_ascii_phone_separators" or proposal.get("column") != "phone":
        return rejected("operation_or_column_not_allowed")
    if proposal.get("arguments") != {}:
        return rejected("arguments_not_empty")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        return rejected("rows_invalid")
    if any("phone" not in row for row in rows):
        return rejected("target_column_missing")
    original = json.loads(json.dumps(rows, ensure_ascii=False))
    preview = json.loads(json.dumps(rows, ensure_ascii=False))
    changed = 0
    for before, after in zip(original, preview):
        if not isinstance(before["phone"], str):
            return rejected("target_cell_not_text")
        after["phone"] = before["phone"].replace(" ", "").replace("-", "")
        if after["phone"] != before["phone"]:
            changed += 1
    original_non_target = [{k:v for k,v in row.items() if k != "phone"} for row in original]
    preview_non_target = [{k:v for k,v in row.items() if k != "phone"} for row in preview]
    invariants = {
        "row_count_unchanged": len(original) == len(preview),
        "column_set_unchanged": [sorted(row.keys()) for row in original] == [sorted(row.keys()) for row in preview],
        "all_non_target_columns_unchanged": original_non_target == preview_non_target,
        "only_ascii_space_and_hyphen_removed": all(
            after["phone"] == before["phone"].replace(" ", "").replace("-", "")
            for before, after in zip(original, preview)
        ),
    }
    if not all(invariants.values()):
        return rejected("invariant_failed")
    return {
        "status":"dry_run_preview",
        "operation":proposal["operation"],
        "target_column":"phone",
        "preview_rows":preview,
        "input_sha256":sha256(canonical(original)),
        "preview_sha256":sha256(canonical(preview)),
        "changed_cell_count":changed,
        "invariants":invariants,
        "execution_started":False,
        "execution_authority":"none",
        "source_modified":False,
        "external_network_request":False,
    }


def main():
    print(canonical(run(json.loads(sys.stdin.read()))))


if __name__ == "__main__":
    main()
