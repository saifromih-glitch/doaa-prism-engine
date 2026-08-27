import json
from pathlib import Path
import doaa_excel_safe_execute as m
payload=json.loads(Path(__file__).with_name("excel-test-input.json").read_text(encoding="utf-8"))
p=payload["proposal"]
print(repr(p.get("column")), repr("\u0627\u0644\u0647\u0627\u062a\u0641"), p.get("column") == "\u0627\u0644\u0647\u0627\u062a\u0641", p.get("operation") == "remove_ascii_phone_separators", p.get("arguments") == {})
print(m.execute(payload))
