import json
import sys

from doaa_proposal_gate import validate_model_output, validate_request


MAX_RAW_LENGTH = 12000


def repair_and_validate(raw_text, request):
    if not isinstance(raw_text, str) or len(raw_text) > MAX_RAW_LENGTH:
        return {"status": "rejected", "reason": "raw_output_invalid", "execution_authority": "none", "repair_id": None, "raw_preserved": True}
    repair_id = None
    candidate = raw_text
    try:
        model_output = json.loads(candidate)
    except json.JSONDecodeError:
        stripped = candidate.strip()
        if stripped.startswith("```json") and stripped.endswith("```"):
            candidate = stripped[7:-3].strip()
            repair_id = "remove_one_complete_json_code_fence"
        elif stripped.startswith("```") and stripped.endswith("```"):
            candidate = stripped[3:-3].strip()
            repair_id = "remove_one_complete_json_code_fence"
        else:
            return {"status": "rejected", "reason": "malformed_json", "execution_authority": "none", "repair_id": None, "raw_preserved": True}
        try:
            model_output = json.loads(candidate)
        except json.JSONDecodeError:
            return {"status": "rejected", "reason": "malformed_json_after_repair", "execution_authority": "none", "repair_id": repair_id, "raw_preserved": True}
    gate_result = validate_model_output(model_output, request)
    gate_result["repair_id"] = repair_id
    gate_result["raw_preserved"] = True
    gate_result["repaired_model_text"] = candidate
    return gate_result


def main():
    payload = json.loads(sys.stdin.read())
    request = payload.get("request")
    raw_text = payload.get("raw_model_text")
    result = repair_and_validate(raw_text, request)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
