import json

from doaa_benchmark import ArabicBenchmark, token_saving_ratio

# These are schema fixtures only; no performance claim is made from them.
cases = [{"case_id": "fixture-1", "language": "ar", "domain": "software", "request": "اشرح اختبار الوحدة", "reference_answer": "إجابة مرجعية"}, {"case_id": "fixture-2", "language": "ar", "domain": "business", "request": "صمم حملة", "reference_answer": "إجابة مرجعية"}]
runs = [{"case_id": "fixture-1", "path": "baseline", "input_tokens": 100, "output_tokens": 200, "latency_ms": 1000, "quality_score": 0.9, "hallucination_flag": False, "safety_pass": True, "human_usefulness": 4}, {"case_id": "fixture-1", "path": "doaa_local", "input_tokens": 20, "output_tokens": 20, "latency_ms": 10, "quality_score": 0.9, "hallucination_flag": False, "safety_pass": True, "human_usefulness": 4}, {"case_id": "fixture-2", "path": "baseline", "input_tokens": 200, "output_tokens": 200, "latency_ms": 1200, "quality_score": 0.8, "hallucination_flag": True, "safety_pass": True, "human_usefulness": 3}]
benchmark = ArabicBenchmark(cases)
summary = benchmark.summarize(runs)
assert summary["status"] == "benchmark_summary_ready"
assert summary["case_count"] == 2
assert summary["paths"]["doaa_local"]["total_tokens"] == 40
assert summary["paths"]["baseline"]["hallucination_rate"] == 0.5
assert summary["claims_allowed"] == "descriptive_only_until_independent_review"
assert token_saving_ratio(400, 40)["saving_ratio"] == 0.9
assert benchmark.summarize([{**runs[0], "quality_score": 2}])["reason"] == "quality_or_latency_invalid"
try:
    ArabicBenchmark([{**cases[0], "language": "en"}])
except ValueError as error:
    assert str(error) == "arabic_case_required"
else:
    raise AssertionError("non-Arabic case accepted")
assert benchmark.summarize([])["reason"] == "benchmark_runs_required"
print(json.dumps({"tests": 8, "status": "passed", "arabic_schema": True, "descriptive_only": True, "synthetic_fixtures_not_claims": True, "execution_authority": "none"}, ensure_ascii=False))
