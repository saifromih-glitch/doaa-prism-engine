import json
import shutil
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_readonly_health import check
root = Path(__file__).parent
ok = check(root)
assert ok["status"] == "health_ok" and ok["writes_files"] is False and ok["automatic_repair"] is False
with tempfile.TemporaryDirectory() as temp:
    copy = Path(temp) / "project"
    shutil.copytree(root, copy, ignore=shutil.ignore_patterns("release", "test-runs-*"))
    missing = copy / "doaa_readonly_health.py"
    missing.unlink()
    blocked = check(copy)
    assert blocked["status"] == "health_blocked" and blocked["writes_files"] is False
with tempfile.TemporaryDirectory() as temp:
    copy = Path(temp) / "project"
    shutil.copytree(root, copy, ignore=shutil.ignore_patterns("release", "test-runs-*"))
    target = copy / "doaa_readonly_health.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n# drift", encoding="utf-8")
    blocked = check(copy)
    assert blocked["status"] == "health_blocked" and any(":hash" in item for item in blocked["failures"])
print(json.dumps({"tests":3,"status":"passed","read_only":True,"automatic_repair":False}, ensure_ascii=False))
