import json
from pathlib import Path

from doaa_semantic_checkpoint import SemanticCheckpointStore

cases = json.loads(Path("benchmark-data/arabicaqa/test-cases.json").read_text(encoding="utf-8"))["cases"]
store = SemanticCheckpointStore()
rows = []
for case in cases:
    request = json.loads(case["request"])
    created = store.create(request["context"])
    record = store._records[created["checkpoint_id"]]
    reference = store.compact_query(created["checkpoint_id"], request["question"])
    payload_text = json.dumps(reference["payload"], ensure_ascii=False, separators=(",", ":"))
    expanded = store.expand(reference["payload"])
    rows.append({"case_id": case["case_id"], "source_chars": len(request["context"]), "reference_chars": len(payload_text), "compression_ratio": round((len(request["context"]) - len(payload_text)) / len(request["context"]), 6), "lossless": expanded.get("text") == request["context"], "segment_count": record["segment_count"]})
report = {"status": "semantic_checkpoint_real_measurement", "dataset": "abdoelsayed/ArabicaQA", "case_count": len(rows), "mean_compression_ratio": round(sum(row["compression_ratio"] for row in rows) / len(rows), 6), "lossless_count": sum(row["lossless"] for row in rows), "all_lossless": all(row["lossless"] for row in rows), "execution_authority": "none", "automatic_execution": False, "rows": rows}
Path("benchmark-data/arabicaqa/semantic-checkpoint-measurement.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "case_count", "mean_compression_ratio", "lossless_count", "all_lossless", "execution_authority")}, ensure_ascii=False))
