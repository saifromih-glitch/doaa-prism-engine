import json
from pathlib import Path

from doaa_answer_verifier import verify_answer

cases = {case["case_id"]: json.loads(case["request"]) for case in json.loads(Path("benchmark-data/arabicaqa/test-cases.json").read_text(encoding="utf-8"))["cases"]}
report = json.loads(Path("benchmark-data/arabicaqa/manus-warm-session-run-v3.json").read_text(encoding="utf-8"))
verdicts = []
for row in report["doaa_rows"]:
    payload = cases[row["case_id"]]
    verdict = verify_answer(payload["question"], payload["context"], row["answer"])
    verdicts.append({"case_id": row["case_id"], "verdict": verdict["status"], "reason": verdict["reason"], "coverage": verdict.get("term_coverage"), "unsupported_terms": verdict.get("unsupported_terms", [])})
counts = {}
for row in verdicts:
    counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
result = {"status": "warm_run_verification_complete", "source_run": "manus-warm-session-run-v3.json", "sample_count": len(verdicts), "verdict_counts": counts, "accepted_for_review": counts.get("supported", 0), "fallback_or_review": len(verdicts) - counts.get("supported", 0), "semantic_truth_claim": False, "automatic_retry": False, "execution_authority": "none", "automatic_execution": False, "rows": verdicts}
Path("benchmark-data/arabicaqa/manus-warm-v3-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ("status", "sample_count", "verdict_counts", "accepted_for_review", "fallback_or_review", "semantic_truth_claim", "execution_authority")}, ensure_ascii=False))
