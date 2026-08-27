import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def request():
    return {
        "protocol": "doaa.alg.v1", "request_id": "req-cli-1",
        "algorithm": {"id": "task.plan.v1", "version": "1"},
        "parameters": {"language": "ar"},
        "context": {"algorithm_refs": [], "user_constraints": []},
        "input": {"kind": "text", "value": "خطط لمهمة"},
        "output_policy": {"format": "natural_language", "language": "ar"},
        "authority": "none", "automatic_execution": False,
    }


def result(r):
    return {"protocol": "doaa.alg.v1", "request_id": r["request_id"], "algorithm": r["algorithm"], "status": "completed", "result": "خطة غير تنفيذية", "authority": "none", "automatic_execution": False}


def run(payload):
    p = subprocess.run([sys.executable, str(ROOT / "doaa_algorithmic_cli.py")], input=json.dumps(payload, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(p.stdout)


def main():
    r = request()
    ok = run({"request": r, "raw_model_result": result(r)})
    assert ok["status"] == "mediation_completed" and ok["rendered"]["text"] == "خطة غير تنفيذية"
    bad = run({"request": r})
    assert bad["status"] == "mediation_blocked" and bad["reason"] == "envelope_schema_invalid"
    bad = run({"request": r, "raw_model_result": {"protocol": "wrong"}})
    assert bad["status"] == "mediation_blocked"
    print('{"tests":3,"status":"passed","network":false,"automatic_execution":false}')


if __name__ == "__main__":
    main()
