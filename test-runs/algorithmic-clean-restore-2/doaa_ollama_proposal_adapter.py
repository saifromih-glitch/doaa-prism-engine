import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse

ID = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")
FORBIDDEN = ("shell_command", "source_code", "generated_code", "secret", "password", "write_path", "subprocess")


def blocked(reason):
    return {"status": "ollama_adapter_blocked", "reason": reason, "execution_authority": "none", "automatic_execution": False, "execution_started": False, "writes_files": False, "source_modified": False}


def is_local_endpoint(endpoint):
    if not isinstance(endpoint, str):
        return False
    try:
        parsed = urlparse(endpoint)
        port = parsed.port
    except ValueError:
        return False
    return (parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}
            and parsed.username is None and parsed.password is None
            and port is not None and 1 <= port <= 65535
            and parsed.path == "/api/generate" and not parsed.query and not parsed.fragment)


def request_proposal(payload, transport=urlopen):
    if not isinstance(payload, dict) or set(payload) != {"message_id", "model_id", "prompt", "execution_authority", "endpoint", "timeout_seconds"}:
        return blocked("envelope_schema_invalid")
    if not ID.fullmatch(payload["message_id"]) or not ID.fullmatch(payload["model_id"]):
        return blocked("identity_invalid")
    if payload["execution_authority"] != "none":
        return blocked("authority_invalid")
    prompt = payload["prompt"]
    if not isinstance(prompt, str) or not 1 <= len(prompt) <= 12000:
        return blocked("prompt_invalid")
    lowered = prompt.lower()
    bad = [marker for marker in FORBIDDEN if marker in lowered]
    if bad:
        return blocked("prohibited_prompt_content")
    endpoint = payload["endpoint"]
    if not is_local_endpoint(endpoint):
        return blocked("local_endpoint_required")
    timeout = payload["timeout_seconds"]
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 30:
        return blocked("timeout_invalid")
    body = json.dumps({"model": payload["model_id"], "prompt": prompt, "stream": False}, ensure_ascii=False).encode("utf-8")
    try:
        response = transport(Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST"), timeout=timeout)
        raw = response.read(262145)
        if len(raw) > 262144:
            return blocked("response_too_large")
        decoded = json.loads(raw.decode("utf-8"))
        text = decoded.get("response") if isinstance(decoded, dict) else None
        if not isinstance(text, str):
            return blocked("response_schema_invalid")
        return {"status": "ollama_raw_proposal_received", "message_id": payload["message_id"], "model_id": payload["model_id"], "raw_response": text, "execution_authority": "none", "automatic_execution": False, "execution_started": False, "writes_files": False, "source_modified": False, "network_scope": "local_ollama_only"}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnicodeError):
        return blocked("local_model_unavailable_or_invalid")


def main():
    print(json.dumps(request_proposal(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
