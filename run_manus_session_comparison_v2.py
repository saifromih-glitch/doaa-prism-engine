"""Live warm-session comparison: one shared context, multiple compact questions."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from openai import OpenAI

DATASET = Path("benchmark-data/arabicaqa/test-cases.json")
OUTPUT = Path("benchmark-data/arabicaqa/manus-warm-session-run-v2.json")
MODEL = os.getenv("DOAA_MODEL", "gpt-5-mini")
SAMPLE_SIZE = int(os.getenv("DOAA_SAMPLE_SIZE", "5"))
if os.getenv("DOAA_RUN_LIVE") != "1":
    raise SystemExit("live_run_requires_DOAA_RUN_LIVE_1")

data = json.loads(DATASET.read_text(encoding="utf-8"))
selected = data["cases"][:SAMPLE_SIZE]
payloads = [json.loads(case["request"]) for case in selected]
client = OpenAI()


def call(messages: list[dict], response_format: dict | None = None) -> dict:
    started = time.perf_counter()
    kwargs = {"model": MODEL, "messages": messages, "max_completion_tokens": 512}
    if response_format:
        kwargs["response_format"] = response_format
    response = client.chat.completions.create(**kwargs)
    usage = response.usage
    return {"content": response.choices[0].message.content or "", "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens, "total_tokens": usage.total_tokens, "latency_ms": round((time.perf_counter() - started) * 1000, 3)}


def overlap(answer: str, reference: str) -> float:
    ref = set(reference.split())
    return round(len(set(answer.split()) & ref) / len(ref), 6) if ref else 0.0

baseline_rows = []
baseline_system = "أجب عن السؤال العربي اعتماداً على السياق فقط. أخرج إجابة عربية موجزة دون شرح."
for case, payload in zip(selected, payloads):
    natural = f"السؤال: {payload['question']}\n\nالسياق:\n{payload['context']}"
    result = call([{"role": "system", "content": baseline_system}, {"role": "user", "content": natural}])
    baseline_rows.append({"case_id": case["case_id"], "reference_answer": case["reference_answer"], "result": result, "reference_overlap": overlap(result["content"], case["reference_answer"])})

context = payloads[0]["context"]
compact = {"v": 1, "ctx": context, "q": [{"i": index, "t": payload["question"]} for index, payload in enumerate(payloads)]}
doaa_system = "doaa.alg.v1|ctx=السياق|q=الأسئلة. لكل i أخرج أقصر إجابة صحيحة مدعومة حرفياً من ctx، دون شرح أو معلومات إضافية. أخرج JSON فقط."
schema = {"type": "json_schema", "json_schema": {"name": "doaa_answers", "strict": True, "schema": {"type": "object", "properties": {"answers": {"type": "array", "items": {"type": "object", "properties": {"i": {"type": "integer"}, "a": {"type": "string"}}, "required": ["i", "a"], "additionalProperties": False}}}, "required": ["answers"], "additionalProperties": False}}}
doaa_result = call([{"role": "system", "content": doaa_system}, {"role": "user", "content": json.dumps(compact, ensure_ascii=False, separators=(",", ":"))}], schema)
parsed = json.loads(doaa_result["content"])
answers = {item["i"]: item["a"] for item in parsed.get("answers", []) if isinstance(item, dict) and isinstance(item.get("i"), int) and isinstance(item.get("a"), str)}
doaa_rows = [{"case_id": case["case_id"], "reference_answer": case["reference_answer"], "answer": answers.get(index, ""), "reference_overlap": overlap(answers.get(index, ""), case["reference_answer"])} for index, case in enumerate(selected)]
base_prompt = sum(row["result"]["prompt_tokens"] for row in baseline_rows)
base_total = sum(row["result"]["total_tokens"] for row in baseline_rows)
report = {"status": "live_warm_session_complete", "model": MODEL, "dataset": data["dataset"], "split": data["split"], "source_sha256": data["source_sha256"], "sample_count": len(selected), "baseline": {"calls": len(baseline_rows), "prompt_tokens": base_prompt, "total_tokens": base_total, "mean_reference_overlap": round(sum(row["reference_overlap"] for row in baseline_rows) / len(baseline_rows), 6)}, "doaa_warm": {"calls": 1, "prompt_tokens": doaa_result["prompt_tokens"], "completion_tokens": doaa_result["completion_tokens"], "total_tokens": doaa_result["total_tokens"], "latency_ms": doaa_result["latency_ms"], "mean_reference_overlap": round(sum(row["reference_overlap"] for row in doaa_rows) / len(doaa_rows), 6)}, "prompt_token_saving_ratio": round((base_prompt - doaa_result["prompt_tokens"]) / base_prompt, 6), "total_token_saving_ratio": round((base_total - doaa_result["total_tokens"]) / base_total, 6), "quality_metric_note": "reference_overlap_is_heuristic_and_not_human_truth_evaluation", "safety_evaluated": False, "execution_authority": "none", "automatic_execution": False, "baseline_rows": baseline_rows, "doaa_rows": doaa_rows}
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: report[key] for key in ("status", "model", "sample_count", "baseline", "doaa_warm", "prompt_token_saving_ratio", "total_token_saving_ratio", "quality_metric_note", "safety_evaluated")}, ensure_ascii=False))
