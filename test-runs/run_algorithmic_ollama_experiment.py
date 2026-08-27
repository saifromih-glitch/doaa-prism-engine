import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://127.0.0.1:11434/api/generate"
MODEL = "rabie-udda-cs:latest"
SYSTEM = "You are a proposal-only assistant. Never use tools, never execute code, never modify files, and return only the requested answer."
ALGORITHMIC_SYSTEM = SYSTEM + " Interpret doaa.alg.v1 messages. For answer.summarize.v1, return JSON with protocol, request_id, algorithm, status, result, authority, automatic_execution."
CASES = [
    {"id": "case-1", "natural": "لخص الفكرة التالية بالعربية في ثلاث جمل مباشرة: دعاء وسيط يحول المطالبات الطبيعية إلى خوارزميات مضغوطة لتقليل التوكنات ثم يعيد النتيجة بلغة طبيعية.", "input": "دعاء وسيط يحول المطالبات الطبيعية إلى خوارزميات مضغوطة لتقليل التوكنات ثم يعيد النتيجة بلغة طبيعية."},
    {"id": "case-2", "natural": "لخص بالعربية في جملتين: الحوكمة تفصل بين اقتراح النموذج والتنفيذ، وتلزم التحقق والمراجعة البشرية قبل الأفعال الحساسة.", "input": "الحوكمة تفصل بين اقتراح النموذج والتنفيذ، وتلزم التحقق والمراجعة البشرية قبل الأفعال الحساسة."},
    {"id": "case-3", "natural": "لخص بالعربية في جملة واحدة: القياس الحقيقي يجب أن يقارن التوكنات والجودة والزمن، وألا يدعي نجاحًا عامًا من تجربة صغيرة.", "input": "القياس الحقيقي يجب أن يقارن التوكنات والجودة والزمن، وألا يدعي نجاحًا عامًا من تجربة صغيرة."},
]


def call(prompt, system):
    body = {"model": MODEL, "system": system, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0, "num_predict": 128}}
    started = time.perf_counter()
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as response:
        data = json.loads(response.read(262144).decode("utf-8"))
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {"elapsed_ms": elapsed_ms, "response": data.get("response", ""), "prompt_eval_count": data.get("prompt_eval_count"), "eval_count": data.get("eval_count"), "eval_duration": data.get("eval_duration"), "load_duration": data.get("load_duration"), "done": data.get("done")}


def main():
    results = []
    for case in CASES:
        natural = call(case["natural"], SYSTEM)
        algorithmic_message = {"protocol": "doaa.alg.v1", "request_id": case["id"], "algorithm": {"id": "answer.summarize.v1", "version": "1"}, "parameters": {"language": "ar", "max_sentences": 3}, "context": {"algorithm_refs": ["answer.summarize.v1"], "user_constraints": []}, "input": {"kind": "text", "value": case["input"]}, "output_policy": {"format": "natural_language", "language": "ar"}, "authority": "none", "automatic_execution": False}
        algorithmic_prompt = json.dumps(algorithmic_message, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        encoded = call(algorithmic_prompt, ALGORITHMIC_SYSTEM)
        results.append({"id": case["id"], "natural": natural, "algorithmic": encoded, "algorithmic_prompt": algorithmic_prompt, "model": MODEL})
    output = {"experiment": "doaa-algorithmic-mediation-v1", "timestamp_utc": datetime.now(timezone.utc).isoformat(), "endpoint_scope": "localhost_only", "model": MODEL, "cases": results, "notes": ["Ollama counters are actual when present.", "Outputs are raw and untrusted.", "This is a small experiment, not a general quality guarantee."]}
    path = ROOT / "test-runs" / "algorithmic-ollama-experiment-results.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "experiment_completed", "model": MODEL, "cases": len(results), "result_file": str(path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
