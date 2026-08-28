import hashlib
import json
from pathlib import Path

SOURCE = Path("benchmark-data/arabicaqa/MRC-test.json")
TARGET = Path("benchmark-data/arabicaqa/test-cases.json")
MAX_CASES = 200
source_bytes = SOURCE.read_bytes()
data = json.loads(source_bytes.decode("utf-8"))
cases = []
for article in data.get("data", []):
    for paragraph in article.get("paragraphs", []):
        context = paragraph.get("context", "")
        for qa in paragraph.get("qas", []):
            answers = qa.get("answers", [])
            if qa.get("is_impossible") or not answers or not context:
                continue
            answer = answers[0].get("text", "")
            question = qa.get("question", "")
            if not isinstance(answer, str) or not answer.strip() or not isinstance(question, str) or not question.strip():
                continue
            cases.append({"case_id": f"arabicaqa-{qa['id']}", "language": "ar", "domain": "general", "request": json.dumps({"question": question, "context": context}, ensure_ascii=False, separators=(",", ":")), "reference_answer": answer, "source_question_id": qa["id"]})
            if len(cases) >= MAX_CASES:
                break
        if len(cases) >= MAX_CASES:
            break
    if len(cases) >= MAX_CASES:
        break
metadata = {"dataset": "abdoelsayed/ArabicaQA", "split": "MRC/test", "source_url": "https://huggingface.co/datasets/abdoelsayed/ArabicaQA", "source_sha256": hashlib.sha256(source_bytes).hexdigest(), "source_bytes": len(source_bytes), "selection": "first 200 answerable records in source order", "case_count": len(cases), "cases": cases}
TARGET.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "built", "case_count": len(cases), "source_sha256": metadata["source_sha256"], "target": str(TARGET)}, ensure_ascii=False))
