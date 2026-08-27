import json
import sys
from pathlib import Path

FORBIDDEN = {"exec", "eval", "subprocess", "socket", "network_request", "secret_access", "overwrite_input", "execute_generated_code"}
REQUIRED = {"contract_id", "operation", "model_execution_authority", "automatic_execution", "fail_closed", "prohibited_actions"}


def validate(path):
    try:
        contract = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"status": "capability_contract_blocked", "reason": "contract_unreadable", "execution_authority": "none"}
    missing = sorted(REQUIRED - set(contract))
    prohibited = set(contract.get("prohibited_actions", []))
    errors = []
    if missing:
        errors.append("required_fields_missing")
    if contract.get("model_execution_authority") != "none":
        errors.append("model_authority_invalid")
    if contract.get("automatic_execution") is not False:
        errors.append("automatic_execution_must_be_false")
    if contract.get("fail_closed") is not True:
        errors.append("fail_closed_required")
    if not FORBIDDEN.issubset(prohibited):
        errors.append("forbidden_actions_incomplete")
    return {"status": "capability_contract_verified" if not errors else "capability_contract_blocked", "contract_id": contract.get("contract_id"), "operation": contract.get("operation"), "errors": errors, "execution_authority": "none", "automatic_execution": False}


def main():
    path = sys.argv[1] if len(sys.argv) == 2 else ""
    print(json.dumps(validate(path), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
