# Doaa examples

The session transport example is a local, model-free preparation example. It demonstrates the envelope that an explicit provider adapter would receive; it does not call a model, network, tool, or executor.

Run the deterministic example from the repository root:

```bash
python3 -c "import json; from doaa_session_transport import LocalSessionTransport; e=json.load(open('examples/session-transport-example.json', encoding='utf-8')); t=LocalSessionTransport(e['session_id'], e['model_language']); print(json.dumps(t.prepare(e['algorithm_message']), ensure_ascii=False, indent=2))"
```

The returned payload includes the handshake on the first request. Subsequent requests in the same `LocalSessionTransport` instance omit it. Provider integrations remain explicit and external to the core.
