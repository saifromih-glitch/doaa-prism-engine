import json
from pathlib import Path

path = Path("benchmark-data/arabicaqa/MRC-test.json")
data = json.loads(path.read_text(encoding="utf-8"))
print(type(data).__name__)
print(sorted(data.keys()) if isinstance(data, dict) else None)
if isinstance(data, dict):
    records = data.get("data")
    print(type(records).__name__, len(records) if isinstance(records, list) else None)
    if records:
        first = records[0]
        print(sorted(first.keys()))
        print(json.dumps(first, ensure_ascii=False)[:2000])
