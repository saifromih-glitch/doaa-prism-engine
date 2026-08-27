import hashlib
import json
import sys
from pathlib import Path


def monitor(root, manifest_path):
    root = Path(root)
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        return {"status":"monitor_alert","reason":"manifest_missing","repair_started":False,"execution_authority":"none"}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {"status":"monitor_alert","reason":"manifest_invalid","repair_started":False,"execution_authority":"none"}
    findings=[]
    for entry in manifest.get("files", []):
        path = root / entry.get("path", "")
        if not path.is_file():
            findings.append({"path":entry.get("path"),"reason":"file_missing"})
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != entry.get("sha256"):
            findings.append({"path":entry.get("path"),"reason":"hash_mismatch"})
    return {"status":"monitor_ok" if not findings else "monitor_alert","findings":findings,"files_checked":len(manifest.get("files",[])),"repair_started":False,"source_modified":False,"execution_authority":"none","automatic_execution":False}


def main():
    print(json.dumps(monitor(sys.argv[1], sys.argv[2]), ensure_ascii=False, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__": main()
