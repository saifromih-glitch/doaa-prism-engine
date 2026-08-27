import json
import re
import sys

REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
FORBIDDEN_KEYS = {"command", "shell", "source_code", "subprocess", "network", "secret", "write_path"}


def classify(envelope):
    if not isinstance(envelope, dict):
        return {"status": "integration_blocked", "reason": "envelope_object_required", "execution_authority": "none", "automatic_execution": False}
    if set(envelope) - {"request_id", "payload", "execution_authority"}:
        return {"status": "integration_blocked", "reason": "extra_fields_rejected", "execution_authority": "none", "automatic_execution": False}
    if not isinstance(envelope.get("request_id"), str) or not REQUEST_ID.fullmatch(envelope["request_id"]):
        return {"status": "integration_blocked", "reason": "request_id_invalid", "execution_authority": "none", "automatic_execution": False}
    if envelope.get("execution_authority") != "none":
        return {"status": "integration_blocked", "reason": "authority_invalid", "execution_authority": "none", "automatic_execution": False}
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        return {"status": "integration_blocked", "reason": "structured_payload_required", "execution_authority": "none", "automatic_execution": False}
    forbidden = sorted(FORBIDDEN_KEYS.intersection(payload))
    if forbidden:
        return {"status": "integration_blocked", "reason": "prohibited_payload_key", "keys": forbidden, "execution_authority": "none", "automatic_execution": False}
    return {"status": "integration_message_accepted_for_governed_flow", "request_id": envelope["request_id"], "payload_keys": sorted(payload), "execution_authority": "none", "automatic_execution": False, "execution_started": False, "source_modified": False}


def main():
    print(json.dumps(classify(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
