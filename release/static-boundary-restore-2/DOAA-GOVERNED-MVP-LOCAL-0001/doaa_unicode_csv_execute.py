import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = ("\u00a0", "\u202f")


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode("utf-8")).hexdigest()


def blocked(reason):
    return {"status":"normalize_unicode_whitespace_blocked","reason":reason,"execution_started":False,"source_modified":False,"model_execution_authority":"none","network_request":False}


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
    if (proposal.get("operation") != "normalize_unicode_whitespace" or proposal.get("arguments") != {} or not isinstance(proposal.get("column"), str) or not proposal.get("column")):
        return blocked("proposal_not_allowed")
    if proposal.get("execution_authority") != "none" or review.get("status") != "accepted_by_human" or review.get("execution_authority") != "none":
        return blocked("human_acceptance_required")
    if review.get("proposal_sha256") != sha(canon(proposal)):
        return blocked("proposal_hash_mismatch")
    if not isinstance(review.get("audit_record_sha256"), str) or len(review["audit_record_sha256"]) != 64:
        return blocked("audit_hash_required")
    preview_hash = review.get("preview_input_sha256")
    if not isinstance(preview_hash, str) or len(preview_hash) != 64 or preview_hash != sha(inp.read_bytes()):
        return blocked("preview_source_hash_required_or_mismatch")
    with inp.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if proposal["column"] not in fields:
            return blocked("target_column_missing")
        before = [dict(row) for row in reader]
    after = [dict(row) for row in before]
    changed = 0
    for row in after:
        old = row[proposal["column"]]
        if not isinstance(old, str):
            return blocked("target_cell_not_text")
        new = old.replace("\u00a0", " ").replace("\u202f", " ")
        if new != old:
            changed += 1
        row[proposal["column"]] = new
    non_target = [name for name in fields if name != proposal["column"] and any(before[i][name] != after[i][name] for i in range(len(before)))]
    only_allowed = all(after[i][proposal["column"]] == before[i][proposal["column"]].replace("\u00a0", " ").replace("\u202f", " ") for i in range(len(before)))
    invariants = {"row_count_unchanged": len(before) == len(after), "column_set_unchanged": fields == list(after[0].keys()) if after else True, "non_target_columns_unchanged": not non_target, "only_allowed_codepoints_replaced": only_allowed}
    if not all(invariants.values()):
        return blocked("invariant_failure")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(after)
    return {"status":"normalize_unicode_whitespace_executed_safe_file","operation":proposal["operation"],"target_column":proposal["column"],"changed_cell_count":changed,"row_count_before":len(before),"row_count_after":len(after),"columns_before":fields,"columns_after":fields,"invariants":invariants,"input_sha256":sha(inp.read_bytes()),"output_sha256":sha(out.read_bytes()),"execution_timestamp_utc":datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),"source_modified":False,"model_execution_authority":"none","network_request":False,"execution_started":True,"output_path":str(out)}


def main():
    print(json.dumps(execute(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
