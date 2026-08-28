import json
from collections import Counter, defaultdict
from pathlib import Path

cases = json.loads(Path("benchmark-data/arabicaqa/test-cases.json").read_text(encoding="utf-8"))["cases"]
groups = defaultdict(list)
for case in cases:
    request = json.loads(case["request"])
    groups[request["context"]].append({"case_id": case["case_id"], "question": request["question"], "reference_answer": case["reference_answer"]})
ranked = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
result = {"dataset": "ArabicaQA", "case_count": len(cases), "unique_contexts": len(groups), "repeated_context_groups": sum(len(items) > 1 for _, items in ranked), "top_groups": [{"context": context, "case_count": len(items), "cases": items} for context, items in ranked[:10]]}
Path("benchmark-data/arabicaqa/recurrent-context-selection.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"dataset": result["dataset"], "case_count": result["case_count"], "unique_contexts": result["unique_contexts"], "repeated_context_groups": result["repeated_context_groups"], "top_group_sizes": [group["case_count"] for group in result["top_groups"]]}, ensure_ascii=False))
