import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent
results = []
for path in sorted(root.glob("test_*.py")):
    try:
        proc = subprocess.run([sys.executable, str(path)], cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=60)
        output = (proc.stdout + proc.stderr).strip().splitlines()
        results.append({"file": path.name, "returncode": proc.returncode, "passed": proc.returncode == 0, "tail": output[-3:]})
    except subprocess.TimeoutExpired as exc:
        results.append({"file": path.name, "returncode": None, "passed": False, "timeout": True, "tail": [str(exc)]})
summary = {
    "test_files": len(results),
    "passed_files": sum(1 for x in results if x["passed"]),
    "failed_or_timeout_files": sum(1 for x in results if not x["passed"]),
    "results": results,
}
(root / "release-acceptance-results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: summary[k] for k in ["test_files", "passed_files", "failed_or_timeout_files"]}, ensure_ascii=False))
