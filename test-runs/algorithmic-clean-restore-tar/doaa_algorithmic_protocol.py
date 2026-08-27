"""Pure, closed-world protocol primitives for Doaa algorithmic mediation."""
from __future__ import annotations

import json
import re
from typing import Any

PROTOCOL = "doaa.alg.v1"
AUTHORITY = "none"
ALGORITHMS = {
    "answer.compose.v1": {"version": "1", "input_kind": "text"},
    "answer.summarize.v1": {"version": "1", "input_kind": "text"},
    "task.plan.v1": {"version": "1", "input_kind": "text"},
}
ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")
LANG_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Z]{2})?$")
FORBIDDEN_KEYS = {
    "shell", "subprocess", "source_code", "generated_code", "tool_call",
    "write_path", "credentials", "secret_access", "network_instruction",
    "model_update", "self_update", "execution_authority",
}
MAX_REQUEST_BYTES = 65536
MAX_RESULT_BYTES = 131072
MAX_DEPTH = 6


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _depth(value: Any, level: int = 0) -> int:
    if isinstance(value, dict):
        return max([level] + [_depth(k, level + 1) for k in value] + [_depth(v, level + 1) for v in value.values()])
    if isinstance(value, list):
        return max([level] + [_depth(v, level + 1) for v in value])
    return level


def _has_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(k) in FORBIDDEN_KEYS or _has_forbidden_key(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_has_forbidden_key(v) for v in value)
    return False


def _valid_json_tree(value: Any) -> bool:
    if value is None or isinstance(value, (str, int, float, bool)):
        return not isinstance(value, float) or value == value
    if isinstance(value, list):
        return all(_valid_json_tree(v) for v in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _valid_json_tree(v) for k, v in value.items())
    return False


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "status": "algorithmic_message_blocked",
        "reason": reason,
        "execution_authority": AUTHORITY,
        "automatic_execution": False,
    }


def _check_common(value: Any, limit: int) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return _blocked("object_required")
    if not _valid_json_tree(value):
        return _blocked("json_value_invalid")
    if _depth(value) > MAX_DEPTH:
        return _blocked("depth_limit_exceeded")
    if _has_forbidden_key(value):
        return _blocked("forbidden_key_detected")
    if len(canonical(value).encode("utf-8")) > limit:
        return _blocked("serialized_size_exceeded")
    return None


def encode_request(request: Any) -> dict[str, Any]:
    """Validate an already classified request and return a canonical algorithm message."""
    common = _check_common(request, MAX_REQUEST_BYTES)
    if common:
        return common
    expected = {"protocol", "request_id", "algorithm", "parameters", "context", "input", "output_policy", "authority", "automatic_execution"}
    if set(request) != expected:
        return _blocked("request_schema_invalid")
    if request["protocol"] != PROTOCOL or not isinstance(request["request_id"], str) or not ID_RE.fullmatch(request["request_id"]):
        return _blocked("request_identity_invalid")
    alg = request["algorithm"]
    if not isinstance(alg, dict) or set(alg) != {"id", "version"} or alg not in [{"id": k, "version": v["version"]} for k, v in ALGORITHMS.items()]:
        return _blocked("algorithm_not_registered")
    if not isinstance(request["parameters"], dict) or not isinstance(request["context"], dict):
        return _blocked("parameters_context_invalid")
    inp = request["input"]
    if not isinstance(inp, dict) or set(inp) != {"kind", "value"} or inp["kind"] != "text" or not isinstance(inp["value"], str) or len(inp["value"]) > 32768:
        return _blocked("input_invalid")
    policy = request["output_policy"]
    if not isinstance(policy, dict) or set(policy) != {"format", "language"} or policy["format"] not in {"natural_language", "structured"} or not isinstance(policy["language"], str) or not LANG_RE.fullmatch(policy["language"]):
        return _blocked("output_policy_invalid")
    if request["authority"] != AUTHORITY or request["automatic_execution"] is not False:
        return _blocked("authority_invalid")
    return {"status": "algorithm_message_valid", "message": json.loads(canonical(request)), "execution_authority": AUTHORITY, "automatic_execution": False}


def validate_result(result: Any, request: dict[str, Any]) -> dict[str, Any]:
    common = _check_common(result, MAX_RESULT_BYTES)
    if common:
        return common
    expected = {"protocol", "request_id", "algorithm", "status", "authority", "automatic_execution"}
    if set(result) - (expected | {"result", "refusal", "evidence_refs"}) or not expected.issubset(result):
        return _blocked("result_schema_invalid")
    if result["protocol"] != PROTOCOL or result["request_id"] != request.get("request_id") or result["algorithm"] != request.get("algorithm"):
        return _blocked("result_binding_mismatch")
    if result["status"] not in {"completed", "incomplete", "refused"}:
        return _blocked("result_status_invalid")
    if result["authority"] != AUTHORITY or result["automatic_execution"] is not False:
        return _blocked("authority_invalid")
    if "result" in result and (not isinstance(result["result"], str) or len(result["result"]) > 65536):
        return _blocked("result_value_invalid")
    if "refusal" in result and (not isinstance(result["refusal"], str) or len(result["refusal"]) > 4096):
        return _blocked("refusal_value_invalid")
    if "evidence_refs" in result and (not isinstance(result["evidence_refs"], list) or len(result["evidence_refs"]) > 32 or not all(isinstance(x, str) and ID_RE.fullmatch(x) for x in result["evidence_refs"])):
        return _blocked("evidence_refs_invalid")
    return {"status": "algorithm_result_valid", "result": json.loads(canonical(result)), "execution_authority": AUTHORITY, "automatic_execution": False}


def render_result(validated: dict[str, Any]) -> dict[str, Any]:
    if validated.get("status") != "algorithm_result_valid":
        return _blocked("validated_result_required")
    result = validated["result"]
    if result["status"] in {"refused", "incomplete"}:
        text = result.get("refusal") or result.get("result") or "النتيجة غير مكتملة."
    else:
        text = result.get("result", "")
    return {"status": "natural_language_rendered", "request_id": result["request_id"], "language": "ar", "text": text, "execution_authority": AUTHORITY, "automatic_execution": False}
