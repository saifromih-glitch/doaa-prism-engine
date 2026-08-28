"""Reproducible, model-agnostic benchmark calculations for Doaa."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.benchmark.v1"
_PATHS = {"baseline", "doaa_local", "doaa_model_assisted"}


class ArabicBenchmark:
    def __init__(self, cases: Any) -> None:
        self.cases = self._validate_cases(cases)

    @staticmethod
    def _validate_cases(cases: Any) -> list[dict[str, Any]]:
        if not isinstance(cases, list) or not cases:
            raise ValueError("benchmark_cases_required")
        required = {"case_id", "language", "domain", "request", "reference_answer"}
        optional = {"source_question_id"}
        seen: set[str] = set()
        normalized = []
        for case in cases:
            if not isinstance(case, dict) or set(case) - (required | optional) or not required.issubset(case):
                raise ValueError("benchmark_case_schema_invalid")
            if not all(isinstance(case[key], str) and case[key].strip() for key in required):
                raise ValueError("benchmark_case_field_invalid")
            if case["language"] != "ar":
                raise ValueError("arabic_case_required")
            if case["case_id"] in seen:
                raise ValueError("duplicate_case_id")
            seen.add(case["case_id"])
            normalized.append(dict(case))
        return normalized

    def summarize(self, runs: Any) -> dict[str, Any]:
        if not isinstance(runs, list) or not runs:
            return _blocked("benchmark_runs_required")
        case_ids = {case["case_id"] for case in self.cases}
        accepted: list[dict[str, Any]] = []
        for run in runs:
            if not isinstance(run, dict):
                return _blocked("run_schema_invalid")
            required = {"case_id", "path", "input_tokens", "output_tokens", "latency_ms", "quality_score", "hallucination_flag", "safety_pass", "human_usefulness"}
            if set(run) - required or not required.issubset(run) or run["case_id"] not in case_ids or run["path"] not in _PATHS:
                return _blocked("run_schema_invalid")
            if not isinstance(run["input_tokens"], int) or not isinstance(run["output_tokens"], int) or run["input_tokens"] < 0 or run["output_tokens"] < 0:
                return _blocked("token_metric_invalid")
            if not isinstance(run["latency_ms"], (int, float)) or run["latency_ms"] < 0 or not isinstance(run["quality_score"], (int, float)) or not 0 <= run["quality_score"] <= 1:
                return _blocked("quality_or_latency_invalid")
            if not isinstance(run["hallucination_flag"], bool) or not isinstance(run["safety_pass"], bool) or not isinstance(run["human_usefulness"], (int, float)) or not 0 <= run["human_usefulness"] <= 5:
                return _blocked("label_metric_invalid")
            accepted.append(dict(run))
        by_path: dict[str, list[dict[str, Any]]] = {path: [] for path in _PATHS}
        for run in accepted:
            by_path[run["path"]].append(run)
        summary = {path: _path_summary(items) for path, items in by_path.items() if items}
        return {"status": "benchmark_summary_ready", "contract": CONTRACT, "case_count": len(self.cases), "run_count": len(accepted), "paths": summary, "claims_allowed": "descriptive_only_until_independent_review", "execution_authority": "none", "automatic_execution": False}


def _path_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    input_tokens = sum(item["input_tokens"] for item in items)
    output_tokens = sum(item["output_tokens"] for item in items)
    total = input_tokens + output_tokens
    return {"runs": len(items), "mean_quality": round(sum(item["quality_score"] for item in items) / len(items), 6), "hallucination_rate": round(sum(item["hallucination_flag"] for item in items) / len(items), 6), "safety_pass_rate": round(sum(item["safety_pass"] for item in items) / len(items), 6), "mean_human_usefulness": round(sum(item["human_usefulness"] for item in items) / len(items), 6), "mean_latency_ms": round(sum(item["latency_ms"] for item in items) / len(items), 6), "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total}


def token_saving_ratio(baseline_total: Any, candidate_total: Any) -> dict[str, Any]:
    if not isinstance(baseline_total, int) or not isinstance(candidate_total, int) or baseline_total <= 0 or candidate_total < 0:
        return _blocked("token_totals_invalid")
    return {"status": "token_comparison_ready", "baseline_total": baseline_total, "candidate_total": candidate_total, "saving": baseline_total - candidate_total, "saving_ratio": round((baseline_total - candidate_total) / baseline_total, 6), "execution_authority": "none", "automatic_execution": False}


def _blocked(reason: str) -> dict[str, Any]:
    return {"status": "benchmark_blocked", "contract": CONTRACT, "reason": reason, "execution_authority": "none", "automatic_execution": False}
