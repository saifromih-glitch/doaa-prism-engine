import hashlib
import json
import sys
from pathlib import Path

def check(root):
    root = Path(root).resolve()
    manifest_path = root / "DOAA-GOVERNED-MVP-0001-manifest.json"
    if not manifest_path.is_file():
        return {"status":"health_blocked","reason":"manifest_missing","writes_files":False,"automatic_repair":False}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, UnicodeError):
        return {"status":"health_blocked","reason":"manifest_invalid","writes_files":False,"automatic_repair":False}
    failures = []
    for entry in manifest.get("files", []):
        path = root / entry.get("path", "")
        if not path.is_file():
            failures.append(entry.get("path", "unknown") + ":missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
            failures.append(entry.get("path", "unknown") + ":hash")
    for key in ("model_execution_authority",):
        if manifest.get(key) != "none": failures.append(key + ":invalid")
    if manifest.get("automatic_execution") is not False: failures.append("automatic_execution:invalid")
    result = {"status":"health_ok" if not failures else "health_blocked","failures":failures,"manifest_files":len(manifest.get("files", [])),"execution_authority":"none","automatic_execution":False,"writes_files":False,"automatic_repair":False,"source_modified":False}
    return result

if __name__ == "__main__":
    print(json.dumps(check(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
