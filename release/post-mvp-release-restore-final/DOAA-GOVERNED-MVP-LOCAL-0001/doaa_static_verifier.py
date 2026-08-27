import json
import re
import sys
from pathlib import Path

FORBIDDEN = ("subprocess", "socket", "eval(", "exec(", "requests.", "urllib.request", "os.system", "os.popen")

def verify(paths):
    findings = []
    for raw in paths:
        path = Path(raw)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            findings.append({"path": str(path), "reason": "unreadable"})
            continue
        for token in FORBIDDEN:
            if re.search(re.escape(token), text):
                findings.append({"path": str(path), "token": token})
    return {"status": "static_verification_passed" if not findings else "static_verification_blocked", "findings": findings, "execution_authority": "none", "automatic_execution": False}

def main():
    print(json.dumps(verify(sys.argv[1:]), ensure_ascii=False, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
