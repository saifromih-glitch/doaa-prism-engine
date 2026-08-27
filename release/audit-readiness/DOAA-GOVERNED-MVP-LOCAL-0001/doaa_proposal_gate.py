import json
import sys

SUPPORTED_OPERATIONS = {
    "1.4": {"remove_ascii_phone_separators", "normalize_ascii_spaces", "trim_ascii_spaces", "tabs_to_ascii_space"}
}
FORBIDDEN_MARKERS = ("http://", "https://", "powershell", "cmd.exe", "shell", "subprocess", "secret", "password")


def _reject(code):
    return {"status": "rejected", "reason": code, "execution_authority": "none"}


def _is_text(value):
    return isinstance(value, str) and not isinstance(value, bool)


def _schema_columns(request):
    schema = request.get("table_schema")
    if not isinstance(schema, list) or len(schema) > 64:
        return None
    columns = {}
    for item in schema:
        if not isinstance(item, dict) or set(item) != {"name", "type"}:
            return None
        if not _is_text(item["name"]) or len(item["name"]) > 128:
            return None
        if item["type"] not in {"text", "number", "boolean", "null"}:
            return None
        columns[item["name"]] = item["type"]
    return columns


def validate_request(request):
    if not isinstance(request, dict) or set(request) != {"goal", "table_schema", "dsl_version"}:
        return _reject("invalid_request_keys")
    if not _is_text(request["goal"]) or not 1 <= len(request["goal"]) <= 1000:
        return _reject("invalid_goal")
    if request["dsl_version"] not in SUPPORTED_OPERATIONS:
        return _reject("unsupported_dsl_version")
    columns = _schema_columns(request)
    if columns is None:
        return _reject("invalid_table_schema")
    return {"status": "request_valid", "columns": columns}


def _contains_forbidden_text(value):
    if not _is_text(value):
        return False
    lowered = value.lower()
    return any(marker in lowered for marker in FORBIDDEN_MARKERS)


def validate_model_output(output, request):
    request_result = validate_request(request)
    if request_result["status"] != "request_valid":
        return request_result
    if not isinstance(output, dict):
        return _reject("output_not_object")
    if output.get("execution_authority") != "none":
        return _reject("execution_authority_not_none")
    kind = output.get("kind")
    if kind == "proposal":
        expected = {"kind", "execution_authority", "operation", "column", "arguments", "rationale"}
        if set(output) != expected:
            return _reject("proposal_keys_invalid")
        if not _is_text(output["operation"]) or output["operation"] not in SUPPORTED_OPERATIONS[request["dsl_version"]]:
            return _reject("operation_not_registered")
        if not _is_text(output["column"]) or request_result["columns"].get(output["column"]) != "text":
            return _reject("column_not_declared_text")
        if not isinstance(output["arguments"], dict) or output["arguments"]:
            return _reject("arguments_invalid")
        if not _is_text(output["rationale"]) or len(output["rationale"]) > 1000 or _contains_forbidden_text(output["rationale"]):
            return _reject("rationale_invalid")
        return {"status": "accepted_proposal", "execution_authority": "none", "proposal": output}
    if kind == "governed_capability_request":
        expected = {"kind", "execution_authority", "requested_goal", "rationale"}
        if set(output) != expected or not _is_text(output["requested_goal"]) or not 1 <= len(output["requested_goal"]) <= 1000:
            return _reject("capability_request_invalid")
        if not _is_text(output["rationale"]) or len(output["rationale"]) > 1000:
            return _reject("rationale_invalid")
        return {"status": "accepted_capability_request", "execution_authority": "none", "request": output}
    if kind == "rejection":
        expected = {"kind", "execution_authority", "rationale"}
        if set(output) != expected or not _is_text(output["rationale"]) or len(output["rationale"]) > 1000:
            return _reject("rejection_invalid")
        return {"status": "accepted_rejection", "execution_authority": "none", "rejection": output}
    return _reject("kind_invalid")


def main():
    payload = json.loads(sys.stdin.read())
    request = payload.get("request")
    output = payload.get("model_output")
    result = validate_model_output(output, request)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
