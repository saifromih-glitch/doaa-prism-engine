import json

from doaa_model_adapter import prepare_request, validate_adapter_result
from doaa_session_transport import LocalSessionTransport


transport = LocalSessionTransport("adapter-test", "ar")
prepared = prepare_request(transport, {"protocol": "doaa.alg.v1", "request_id": "a1", "authority": "none", "automatic_execution": False})
assert prepared["status"] == "transport_payload_ready"
assert prepared["payload"]["handshake"] is not None

accepted = validate_adapter_result({"protocol": "doaa.alg.v1", "status": "OK", "authority": "none", "automatic_execution": False, "result": "نص"})
assert accepted["status"] == "adapter_result_accepted"
blocked_protocol = validate_adapter_result({"protocol": "other", "status": "OK", "authority": "none", "automatic_execution": False})
assert blocked_protocol["status"] == "adapter_result_blocked"
blocked_authority = validate_adapter_result({"protocol": "doaa.alg.v1", "status": "OK", "authority": "execute", "automatic_execution": True})
assert blocked_authority["status"] == "adapter_result_blocked"
blocked_shape = validate_adapter_result([])
assert blocked_shape["status"] == "adapter_result_blocked"
print(json.dumps({"tests": 5, "status": "passed", "adapter_invocation": "explicit_only", "fail_closed": True, "execution_authority": "none"}, ensure_ascii=False))
