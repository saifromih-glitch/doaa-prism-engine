import json
from pathlib import Path

from doaa_answer_verifier import verify_answer

report = json.loads(Path("benchmark-data/arabicaqa/manus-recurrent-run.json").read_text(encoding="utf-8"))
rows = []
for item in report["doaa_rows"]:
    expanded = item["expanded_reference"]
    verdict = verify_answer(expanded.get("question", ""), expanded.get("text", ""), item["answer"])
    rows.append({"case_id": item["case_id"], "verdict": verdict["status"], "reason": verdict.get("reason"), "coverage": verdict.get("term_coverage"), "unsupported_terms": verdict.get("unsupported_terms", [])})
counts = {}
for row in rows:
    counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
result = {"status": "recurrent_answer_verification_complete", "sample_count": len(rows), "verdict_counts": counts, "accepted_for_review": counts.get("supported", 0), "fallback_or_review": len(rows) - counts.get("supported", 0), "semantic_truth_claim": False, "automatic_retry": False, "execution_authority": "none", "automatic_execution": False, "rows": rows}
Path("benchmark-data/arabicaqa/manus-recurrent-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ("status", "sample_count", "verdict_counts", "accepted_for_review", "fallback_or_review", "execution_authority")}, ensure_ascii=False))
