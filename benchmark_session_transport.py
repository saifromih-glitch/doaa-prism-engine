import json
from pathlib import Path
from doaa_session_transport import LocalSessionTransport, _estimate_tokens

messages = [{"protocol": "doaa.alg.v1", "request_id": f"bench-{i:02d}", "algorithm": {"id": "answer.summarize.v1", "version": "1"}, "parameters": {"language": "ar", "mode": "faithful"}, "authority": "none", "automatic_execution": False} for i in range(1, 21)]
transport = LocalSessionTransport("benchmark-session", "ar")
warm_payload_tokens = []
for item in messages:
    result = transport.prepare(item)
    assert result["status"] == "transport_payload_ready"
    warm_payload_tokens.append(_estimate_tokens(result["payload"]))
handshake = transport.session_state["handshake"]
cold_payload_tokens = [_estimate_tokens({"session_id": "benchmark-session", "handshake": handshake, "message": item}) for item in messages]
summary = {"requests": 20, "cold_proxy_tokens": sum(cold_payload_tokens), "warm_proxy_tokens": sum(warm_payload_tokens), "proxy_saving_tokens": sum(cold_payload_tokens)-sum(warm_payload_tokens), "proxy_saving_pct": round((sum(cold_payload_tokens)-sum(warm_payload_tokens))/sum(cold_payload_tokens)*100, 2), "handshakes_sent": transport.metrics()["handshakes"], "note": "proxy estimate only; provider usage requires a real session-aware adapter", "execution_authority": "none", "automatic_execution": False}
Path("session-transport-benchmark.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
