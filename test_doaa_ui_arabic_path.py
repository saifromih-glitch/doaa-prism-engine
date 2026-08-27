import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_daily_ui import preview_for_ui
root=Path(__file__).parent/"ui-arabic-trial"; root.mkdir(exist_ok=True)
missing=root/"missing.xlsx"
try: preview_for_ui(str(missing),"trim_ascii_spaces","الهاتف","فواتير"); raise AssertionError("expected block")
except ValueError as exc: assert "قراءة الملف" in str(exc)
print(json.dumps({"tests":1,"status":"passed","ui_arabic_message":"ok"},ensure_ascii=False))
