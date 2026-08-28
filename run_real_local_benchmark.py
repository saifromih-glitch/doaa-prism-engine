import hashlib
import json
from pathlib import Path

from doaa_algorithm_library import AlgorithmLibrary
from doaa_multi_source_coordinator import MultiSourceCoordinator
from doaa_runtime import DoaaRuntime
from doaa_token_metrics import estimate_units

DATASET = Path("benchmark-data/arabicaqa/test-cases.json")
OUTPUT = Path("benchmark-data/arabicaqa/local-runtime-run.json")
data = json.loads(DATASET.read_text(encoding="utf-8"))
algorithms = AlgorithmLibrary()
runtime = DoaaRuntime(MultiSourceCoordinator(algorithms))
rows = []
for case in data["cases"]:
    request = json.loads(case["request"])
    result = runtime.prepare({"request": request, "library": "general", "algorithm_id": "question_answering.mrc.v1", "source_request": request})
    prompt_text = case["request"]
    rows.append({"case_id": case["case_id"], "route_status": result.get("route", {}).get("status"), "next_action": result.get("next_action"), "estimated_input_units": estimate_units(prompt_text), "model_called": False, "source_question_id": case.get("source_question_id")})
route_counts = {}
for row in rows:
    route_counts[row["route_status"]] = route_counts.get(row["route_status"], 0) + 1
report = {"status": "real_local_runtime_run", "dataset": data["dataset"], "split": data["split"], "source_sha256": data["source_sha256"], "case_count": len(rows), "route_counts": route_counts, "local_reuse_rate": round(route_counts.get("route_local_algorithm", 0) / len(rows), 6), "model_calls": 0, "estimated_input_units": sum(row["estimated_input_units"] for row in rows), "estimator": "unicode_word_punctuation_proxy", "performance_claim": False, "quality_evaluated": False, "execution_authority": "none", "automatic_execution": False, "rows": rows}
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "dataset", "split", "case_count", "route_counts", "local_reuse_rate", "model_calls", "estimated_input_units", "performance_claim", "quality_evaluated", "execution_authority")}, ensure_ascii=False))
