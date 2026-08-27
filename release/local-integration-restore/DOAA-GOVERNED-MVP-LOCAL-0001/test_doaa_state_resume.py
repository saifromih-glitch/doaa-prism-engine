import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_state_resume import validate_state
base={"status":"stable","facts":["tests pass"],"decisions":["authority none"],"checked":["manifest"],"changed":[],"unverified":["ollama live"],"risks":["local environment"],"next_step":"run next governed acceptance"}
ok=validate_state(base)
assert ok["status"] == "state_ready" and ok["execution_started"] is False
extra=dict(base);extra["write_path"]="x"
assert validate_state(extra)["status"] == "state_blocked"
missing=dict(base);missing.pop("risks")
assert validate_state(missing)["status"] == "state_blocked"
empty=dict(base);empty["next_step"]=""
assert validate_state(empty)["status"] == "state_blocked"
wrong=dict(base);wrong["facts"]="not-list"
assert validate_state(wrong)["status"] == "state_blocked"
print(json.dumps({"tests":5,"status":"passed","one_next_step":True,"automatic_execution":False}, ensure_ascii=False))
