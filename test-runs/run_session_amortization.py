import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://127.0.0.1:11434/api/generate"
MODEL = "rabie-udda-cs:latest"
HANDSHAKE = "You are proposal-only. Interpret DOAA/1 compact messages. Never use tools, never execute code, never modify files. Return only the requested answer. R1 means summarize faithfully, preserve facts, in the requested language, with no tools."
CASES = [
    "لخص بالعربية في جملة: دعاء يقلل تكرار التعليمات عبر لغة وسيطة.",
    "لخص بالعربية في جملة: الحوكمة تفصل الاقتراح عن التنفيذ وتطلب مراجعة بشرية.",
    "لخص بالعربية في جملة: يجب قياس التوفير بدل افتراضه.",
]


def call(prompt, context=None, predict=64):
    body = {"model": MODEL, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0, "num_predict": predict}}
    if context:
        body["context"] = context
    started = time.perf_counter()
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as response:
        data = json.loads(response.read(262144).decode("utf-8"))
    return {"elapsed_ms": round((time.perf_counter() - started) * 1000, 2), "response": data.get("response", ""), "prompt_eval_count": data.get("prompt_eval_count"), "eval_count": data.get("eval_count"), "context": data.get("context"), "done": data.get("done")}


def main():
    natural = [call(p) for p in CASES]
    handshake_prompt = HANDSHAKE + "\nHandshake acknowledged with token H1."
    first = call(handshake_prompt, predict=8)
    context = first.get("context")
    algorithmic = []
    for i, text in enumerate(CASES, 1):
        msg = json.dumps({"p":"doaa.alg.v1","r":"R1","i":i,"l":"ar","x":text,"e":False}, ensure_ascii=False, separators=(",", ":"))
        item = call("H1 " + msg, context=context, predict=96) if context else call(HANDSHAKE + "\n" + msg, predict=96)
        context = item.get("context") or context
        item.pop("context", None)
        algorithmic.append({"prompt": msg, **item})
    first.pop("context", None)
    result = {"experiment":"doaa-session-amortization-v1","timestamp_utc":datetime.now(timezone.utc).isoformat(),"model":MODEL,"endpoint_scope":"localhost_only","natural":natural,"handshake":{"prompt":handshake_prompt,**first},"algorithmic":algorithmic,"notes":["Ollama prompt_eval_count is the local runtime counter.","Context continuation support is recorded by whether a context was returned.","This measures local processing, not paid API billing.","Outputs remain untrusted and were not treated as protocol-valid results."]}
    out = ROOT / "test-runs" / "doaa-session-amortization-results.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status":"session_experiment_completed","cases":len(CASES),"context_supported":bool(context),"result_file":str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
