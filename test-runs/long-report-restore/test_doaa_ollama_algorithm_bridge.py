import json
from io import BytesIO
from doaa_ollama_algorithm_bridge import call_and_mediate, prepare


def req():
    return {"protocol":"doaa.alg.v1","request_id":"req-bridge-1","algorithm":{"id":"answer.summarize.v1","version":"1"},"parameters":{"language":"ar"},"context":{"algorithm_refs":[],"user_constraints":[]},"input":{"kind":"text","value":"نص"},"output_policy":{"format":"natural_language","language":"ar"},"authority":"none","automatic_execution":False}


def transport(request, timeout):
    body = json.loads(request.data.decode("utf-8"))
    result = {"protocol":"doaa.alg.v1","request_id":"req-bridge-1","algorithm":{"id":"answer.summarize.v1","version":"1"},"status":"completed","result":"ملخص من Ollama","authority":"none","automatic_execution":False}
    assert body["stream"] is False
    assert body["prompt"].startswith("{\"algorithm\"")
    return BytesIO(json.dumps({"response": json.dumps(result, ensure_ascii=False)}, ensure_ascii=False).encode("utf-8"))


def main():
    r = req()
    prepared = prepare(r, "msg-1", "local-model", "http://127.0.0.1:11434/api/generate")
    assert prepared["status"] == "ollama_algorithm_request_prepared"
    done = call_and_mediate(r, "msg-1", "local-model", "http://127.0.0.1:11434/api/generate", transport)
    assert done["status"] == "ollama_bridge_completed"
    assert done["mediation"]["rendered"]["text"] == "ملخص من Ollama"
    assert done["model_result_trusted"] is False
    bad = call_and_mediate(r, "msg-1", "local-model", "https://example.com/api/generate", transport)
    assert bad["status"] == "ollama_bridge_blocked"
    print('{"tests":3,"status":"passed","local_only":true,"model_result_trusted":false,"authority":"none"}')


if __name__ == "__main__":
    main()
