import json
import re

REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
FORBIDDEN_KEYS = {"command", "shell", "source_code", "subprocess", "network", "secret", "write_path"}
MAX_PAYLOAD_BYTES = 16384
MAX_DEPTH = 8


def _payload_safe(value, depth=0):
    if depth > MAX_DEPTH:
        return False
    if isinstance(value, dict):
        return all(isinstance(k, str) and k not in FORBIDDEN_KEYS and _payload_safe(v, depth + 1) for k, v in value.items())
    if isinstance(value, list):
        return all(_payload_safe(item, depth + 1) for item in value)
    return value is None or isinstance(value, (str, int, float, bool))


def _blocked(reason, **extra):
    return {"status": "integration_blocked", "reason": reason, **extra, "execution_authority": "none", "automatic_execution": False}


def classify(envelope):
    if not isinstance(envelope, dict):
        return _blocked("envelope_object_required")
    if set(envelope) - {"request_id", "payload", "execution_authority"}:
        return _blocked("extra_fields_rejected")
    request_id = envelope.get("request_id")
    if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
        return _blocked("request_id_invalid")
    if envelope.get("execution_authority") != "none":
        return _blocked("authority_invalid")
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        return _blocked("structured_payload_required")
    try:
        payload_size = len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    except (TypeError, ValueError, UnicodeError):
        return _blocked("payload_json_invalid")
    if payload_size > MAX_PAYLOAD_BYTES:
        return _blocked("payload_too_large")
    if not _payload_safe(payload):
        return _blocked("payload_structure_invalid")
    return {"status": "integration_message_accepted_for_governed_flow", "request_id": request_id, "payload_keys": sorted(payload), "payload_bytes": payload_size, "execution_authority": "none", "automatic_execution": False, "execution_started": False, "source_modified": False}


def main():
    print(json.dumps(classify(json.loads(__import__("sys").stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

