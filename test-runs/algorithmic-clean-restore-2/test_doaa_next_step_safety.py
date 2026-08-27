import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_next_step_safety import validate_next_step
ok=validate_next_step("مراجعة تقرير القبول")
assert ok["status"] == "next_step_verified" and ok["descriptive_only"] is True and ok["execution_started"] is False
assert validate_next_step("")["status"] == "next_step_blocked"
assert validate_next_step("خطوة أولى\nخطوة ثانية")["status"] == "next_step_blocked"
assert validate_next_step("execute shell command")["status"] == "next_step_blocked"
assert validate_next_step(None)["status"] == "next_step_blocked"
print(json.dumps({"tests":5,"status":"passed","single_descriptive_step":True,"automatic_execution":False}, ensure_ascii=False))
