import json

from doaa_session_transport import LocalSessionTransport


def message(request_id: str) -> dict:
    return {"protocol": "doaa.alg.v1", "request_id": request_id, "algorithm": {"id": "answer.compose.v1", "version": "1"}, "authority": "none", "automatic_execution": False}


t = LocalSessionTransport("test-session", "ar")
first = t.prepare(message("r1"))
assert first["status"] == "transport_payload_ready"
assert first["handshake_sent"] is True
assert first["execution_authority"] == "none"
second = t.prepare(message("r2"))
assert second["status"] == "transport_payload_ready"
assert second["handshake_sent"] is False
assert second["payload"]["handshake"] is None
assert t.metrics()["handshakes"] == 1
assert t.metrics()["requests"] == 2
assert t.metrics()["automatic_execution"] is False
closed = t.close()
assert closed["status"] == "session_closed"
blocked = t.prepare(message("r3"))
assert blocked["status"] == "transport_blocked"
assert blocked["reason"] == "session_closed"
invalid = LocalSessionTransport("bad id", "ar")
assert invalid.prepare(message("r4"))["status"] == "transport_blocked"
print(json.dumps({"tests": 10, "status": "passed", "handshake_once": True, "reuse": True, "fail_closed": True, "execution_authority": "none"}, ensure_ascii=False))
