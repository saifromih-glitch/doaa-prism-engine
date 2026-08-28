import json
from pathlib import Path

from doaa_benchmark import ArabicBenchmark

path = Path("benchmark-data/arabicaqa/test-cases.json")
data = json.loads(path.read_text(encoding="utf-8"))
benchmark = ArabicBenchmark(data["cases"])
assert len(benchmark.cases) == data["case_count"] == 200
assert data["dataset"] == "abdoelsayed/ArabicaQA"
assert all(case["language"] == "ar" for case in benchmark.cases)
assert all(case.get("source_question_id") for case in benchmark.cases)
print(json.dumps({"status": "real_dataset_validated", "dataset": data["dataset"], "split": data["split"], "case_count": len(benchmark.cases), "source_sha256": data["source_sha256"], "performance_claim": False}, ensure_ascii=False))
