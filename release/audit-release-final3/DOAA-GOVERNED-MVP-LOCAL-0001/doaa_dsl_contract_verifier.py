import json
from pathlib import Path

REQUIRED = {"contract_id", "operation", "dsl_version", "allowed_columns", "transformation", "preserve_non_target_columns", "preserve_row_count", "preserve_column_set", "output_policy", "model_execution_authority", "automatic_execution", "network_request", "fail_closed", "prohibited_actions"}
REQUIRED_PROHIBITED = {"infer_column", "modify_other_columns", "overwrite_input", "generated_code", "network_request", "secret_access"}


def verify_contract(path, operation):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "contract_rejected", "reason": "contract_read_failure", "execution_authority": "none"}
    missing = sorted(REQUIRED - set(data))
    if missing:
        return {"status": "contract_rejected", "reason": "required_fields_missing", "missing": missing, "execution_authority": "none"}
    if data.get("operation") != operation:
        return {"status": "contract_rejected", "reason": "operation_mismatch", "execution_authority": "none"}
    prohibited = set(data.get("prohibited_actions", []))
    required_without_code = REQUIRED_PROHIBITED - {"generated_code"}
    if not required_without_code.issubset(prohibited) or not ({"generated_code", "execute_generated_code"} & prohibited):
        return {"status": "contract_rejected", "reason": "governance_prohibitions_incomplete", "execution_authority": "none"}
    if data.get("model_execution_authority") != "none" or data.get("automatic_execution") is not False or data.get("network_request") is not False or data.get("fail_closed") is not True or data.get("output_policy") != "new_output_only":
        return {"status": "contract_rejected", "reason": "governance_flags_invalid", "execution_authority": "none"}
    return {"status": "contract_verified", "operation": operation, "contract_id": data["contract_id"], "dsl_version": data["dsl_version"], "execution_authority": "none", "automatic_execution": False}


if __name__ == "__main__":
    import sys
    print(json.dumps(verify_contract(sys.argv[1], sys.argv[2]), ensure_ascii=False))
