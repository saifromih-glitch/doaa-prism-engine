import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from doaa_dsl_contract_verifier import verify_contract

SIGNATURE_FIELDS = ("operation", "column", "worksheet", "dsl_version")
ALLOWED_EXECUTION_STATUSES = {"executed_safe_file", "space_normalize_executed_safe_file", "excel_executed_safe_file", "normalize_unicode_whitespace_executed_safe_file", "normalize_unicode_xlsx_executed_safe_file"}
CONTRACT_BY_OPERATION = {"normalize_ascii_spaces": "CONTRACT-DSL-SPACE-NORMALIZE-0001.json", "trim_ascii_spaces": "CONTRACT-DSL-TRIM-ASCII-SPACES-0001.json", "remove_ascii_phone_separators": "CONTRACT-DSL-PHONE-SEPARATORS-0001.json", "tabs_to_ascii_space": "CONTRACT-DSL-TABS-TO-SPACE-0001.json", "normalize_unicode_whitespace": "CONTRACT-DSL-UNICODE-WHITESPACE-0001.json"}


def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def signature(proposal): return {field: proposal.get(field) for field in SIGNATURE_FIELDS}
def signature_sha256(proposal): return hashlib.sha256(canonical(signature(proposal)).encode("utf-8")).hexdigest()
def _record_is_valid(record): return record.get("record_type") == "approved_algorithm" and record.get("human_review_status") == "accepted_by_human" and record.get("execution_status") in ALLOWED_EXECUTION_STATUSES and record.get("execution_authority") == "none" and record.get("automatic_execution") is False and len(record.get("signature_sha256", "")) == 64


def register(path, proposal, human_review, execution_receipt):
    operation = proposal.get("operation") if isinstance(proposal, dict) else None
    contract_name = CONTRACT_BY_OPERATION.get(operation)
    contract_result = None
    if contract_name:
        contract_result = verify_contract(Path(__file__).parent / contract_name, operation)
        if contract_result.get("status") != "contract_verified":
            return {"status": "registry_rejected", "reason": "contract_verification_failed", "contract_reason": contract_result.get("reason"), "execution_authority": "none"}
    if human_review.get("status") != "accepted_by_human": return {"status":"registry_rejected","reason":"human_acceptance_required","execution_authority":"none"}
    if execution_receipt.get("status") not in ALLOWED_EXECUTION_STATUSES: return {"status":"registry_rejected","reason":"approved_execution_receipt_required","execution_authority":"none"}
    record = {"record_type":"approved_algorithm","signature":signature(proposal),"signature_sha256":signature_sha256(proposal),"human_review_status":human_review["status"],"execution_status":execution_receipt["status"],"execution_authority":"none","automatic_execution":False,"registered_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    if contract_result: record["contract_id"] = contract_result["contract_id"]
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True); existing = lookup_all(target)
    if any(r.get("signature_sha256") == record["signature_sha256"] for r in existing): return {"status":"registry_duplicate","reason":"signature_already_registered","signature_sha256":record["signature_sha256"],"execution_authority":"none"}
    with target.open("a", encoding="utf-8", newline="\n") as handle: handle.write(canonical(record) + "\n")
    return {"status":"registered","signature_sha256":record["signature_sha256"],"contract_id":record.get("contract_id"),"execution_authority":"none","automatic_execution":False}


def lookup_all(path):
    target = Path(path)
    if not target.is_file(): return []
    records = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            record = json.loads(line)
            if _record_is_valid(record): records.append(record)
        except json.JSONDecodeError: continue
    return records


def lookup(path, proposal):
    sig = signature_sha256(proposal)
    for record in lookup_all(path):
        if record.get("signature_sha256") == sig: return {"status":"cache_hit","record":record,"execution_authority":"none","automatic_execution":False}
    return {"status":"cache_miss","reason":"exact_signature_not_found","execution_authority":"none","automatic_execution":False}
