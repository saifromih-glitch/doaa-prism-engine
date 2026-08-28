"""Explicit live comparison runner for Manus-compatible chat models.

Requires DOAA_RUN_LIVE=1. It makes no web calls and writes raw outputs locally.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from openai import OpenAI

DATASET = Path("benchmark-data/arabicaqa/test-cases.json")
OUTPUT = Path("benchmark-data/arabicaqa/manus-comparison-run.json")
MODEL = os.getenv("DOAA_MODEL", "gpt-5-mini")
SAMPLE_SIZE = int(os.getenv("DOAA_SAMPLE_SIZE", "5"))

if os.getenv("DOAA_RUN_LIVE") != "1":
    raise SystemExit("live_run_requires_DOAA_RUN_LIVE_1")

data = json.loads(DATASET.read_text(encoding="utf-8"))
client = OpenAI()
selected = data["cases"][:SAMPLE_SIZE]

baseline_system = "أجب عن السؤال العربي اعتماداً على السياق فقط. إذا لم توجد الإجابة في السياق فقل: لا أعلم من السياق. أخرج إجابة عربية موجزة دون شرح لطريقة العمل."
doaa_system = "بروتوكول doaa.alg.v1. فك JSON التالي: q هو السؤال، c هو السياق، r هو الجواب المرجعي للاختبار فقط ولا تستخدمه في الإجابة. أجب عن q اعتماداً على c فقط. إذا لم توجد الإجابة فقل: لا أعلم من السياق. أخرج إجابة عربية موجزة فقط."


def request_with_usage(messages: list[dict[str, str]]) -> dict:
    started = time.perf_counter()
    response = client.chat.completions.create(model=MODEL, messages=messages, max_completion_tokens=256)
    elapsed = round((time.perf_counter() - started) * 1000, 3)
    usage = response.usage
    return {"answer": response.choices[0].message.content or "", "prompt_tokens": getattr(usage, "prompt_tokens", None), "completion_tokens": getattr(usage, "completion_tokens", None), "total_tokens": getattr(usage, "total_tokens", None), "latency_ms": elapsed, "finish_reason": response.choices[0].finish_reason}


def overlap_score(answer: str, reference: str) -> float:
    answer_terms = set(answer.split())
    reference_terms = set(reference.split())
    if not reference_terms:
        return 0.0
    return round(len(answer_terms & reference_terms) / len(reference_terms), 6)

rows = []
for case in selected:
    payload = json.loads(case["request"])
    natural = f"السؤال: {payload['question']}\n\nالسياق:\n{payload['context']}"
    compact = json.dumps({"v": 1, "q": payload["question"], "c": payload["context"]}, ensure_ascii=False, separators=(",", ":"))
    baseline = request_with_usage([{"role": "system", "content": baseline_system}, {"role": "user", "content": natural}])
    doaa = request_with_usage([{"role": "system", "content": doaa_system}, {"role": "user", "content": compact}])
    rows.append({"case_id": case["case_id"], "source_question_id": case.get("source_question_id"), "baseline_input_chars": len(natural), "doaa_input_chars": len(compact), "reference_answer": case["reference_answer"], "baseline": {**baseline, "reference_overlap": overlap_score(baseline["answer"], case["reference_answer"])}, "doaa": {**doaa, "reference_overlap": overlap_score(doaa["answer"], case["reference_answer"])}})


def totals(path: str) -> dict:
    values = [row[path] for row in rows]
    return {"prompt_tokens": sum(item["prompt_tokens"] or 0 for item in values), "completion_tokens": sum(item["completion_tokens"] or 0 for item in values), "total_tokens": sum(item["total_tokens"] or 0 for item in values), "mean_latency_ms": round(sum(item["latency_ms"] for item in values) / len(values), 3), "mean_reference_overlap": round(sum(item["reference_overlap"] for item in values) / len(values), 6)}

base_total = totals("baseline")
doaa_total = totals("doaa")
report = {"status": "live_comparison_complete", "model": MODEL, "dataset": data["dataset"], "split": data["split"], "source_sha256": data["source_sha256"], "sample_count": len(rows), "baseline": base_total, "doaa": doaa_total, "prompt_token_saving_ratio": round((base_total["prompt_tokens"] - doaa_total["prompt_tokens"]) / base_total["prompt_tokens"], 6) if base_total["prompt_tokens"] else None, "total_token_saving_ratio": round((base_total["total_tokens"] - doaa_total["total_tokens"]) / base_total["total_tokens"], 6) if base_total["total_tokens"] else None, "quality_metric_note": "reference_overlap_is_heuristic_and_not_human_truth_evaluation", "model_calls": len(rows) * 2, "raw_output_sha256": hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(), "execution_authority": "none", "automatic_execution": False, "rows": rows}
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: report[key] for key in ("status", "model", "sample_count", "baseline", "doaa", "prompt_token_saving_ratio", "total_token_saving_ratio", "quality_metric_note", "model_calls", "execution_authority")}, ensure_ascii=False))
