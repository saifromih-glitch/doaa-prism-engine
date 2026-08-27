import importlib.util
import json
from pathlib import Path

path = Path(__file__).with_name("doaa_daily_ui.py")
spec = importlib.util.spec_from_file_location("doaa_daily_ui", path)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
root = path.parent / "test-runs-ui"; root.mkdir(exist_ok=True)
req = mod.build_request(str(root / "input.csv"), str(root / "output.csv"), "remove_ascii_phone_separators", "phone")
assert req["ui_mode"] == "request_builder_only"
assert req["human_review"]["status"] == "pending_user_review"
assert req["execution_started"] is False
assert req["proposal"]["execution_authority"] == "none"
assert req["output_path"].endswith("output.csv")
try:
    mod.build_request(str(root / "same.csv"), str(root / "same.csv"), "remove_ascii_phone_separators", "phone")
except ValueError as exc:
    assert "ملفًا جديدًا" in str(exc)
else:
    raise AssertionError("same input/output was accepted")
try:
    mod.build_request("", str(root / "output.csv"), "remove_ascii_phone_separators", "phone")
except ValueError:
    pass
else:
    raise AssertionError("missing input was accepted")
print(json.dumps({"tests":3,"status":"passed","request_only":True,"execution_started":False}, ensure_ascii=False, separators=(",", ":")))
