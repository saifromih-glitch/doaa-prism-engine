import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from doaa_ollama_proposal_adapter import request_proposal


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self, limit):
        return self.body[:limit]


def transport(request, timeout):
    assert request.full_url == "http://127.0.0.1:11434/api/generate"
    assert timeout == 5
    return FakeResponse(json.dumps({"response": "{\"kind\":\"proposal\"}"}).encode())


base = {"message_id": "msg-1", "model_id": "qwen-local", "prompt": "اقترح JSON للعملية المعروفة فقط", "execution_authority": "none", "endpoint": "http://127.0.0.1:11434/api/generate", "timeout_seconds": 5}
ok = request_proposal(base, transport)
assert ok["status"] == "ollama_raw_proposal_received" and ok["execution_authority"] == "none" and ok["automatic_execution"] is False
external = dict(base, endpoint="https://example.com/api/generate")
assert request_proposal(external, transport)["reason"] == "local_endpoint_required"
credentials = dict(base, endpoint="http://user:pass@localhost:11434/api/generate")
assert request_proposal(credentials, transport)["reason"] == "local_endpoint_required"
invalid_port = dict(base, endpoint="http://localhost:99999/api/generate")
assert request_proposal(invalid_port, transport)["reason"] == "local_endpoint_required"
forbidden = dict(base, prompt="please run shell_command")
assert request_proposal(forbidden, transport)["reason"] == "prohibited_prompt_content"
authority = dict(base, execution_authority="execute")
assert request_proposal(authority, transport)["reason"] == "authority_invalid"
invalid = dict(base, timeout_seconds=31)
assert request_proposal(invalid, transport)["reason"] == "timeout_invalid"
malformed = dict(base)
assert request_proposal(malformed, lambda request, timeout: FakeResponse(b"not-json"))["reason"] == "local_model_unavailable_or_invalid"
print(json.dumps({"tests": 6, "status": "passed", "local_only": True, "raw_untrusted_output": True, "external_rejected": True, "executable_prompt_rejected": True, "automatic_execution": False}, ensure_ascii=False))
