import json
import sys

def verify(payload):
    required = {"state_summary", "run_report", "health_report"}
    if not isinstance(payload, dict) or set(payload) != required:
        return {"status":"evidence_blocked","reason":"schema_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    state = payload["state_summary"]; run = payload["run_report"]; health = payload["health_report"]
    if not isinstance(state, dict) or not isinstance(run, dict) or not isinstance(health, dict):
        return {"status":"evidence_blocked","reason":"summary_type_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if not isinstance(state.get("next_step"), str) or not state["next_step"].strip():
        return {"status":"evidence_blocked","reason":"next_step_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    for name, item in (("run_report", run), ("health_report", health)):
        if item.get("execution_authority", "none") != "none" or item.get("automatic_execution", False) is not False or item.get("automatic_repair", False) is not False:
            return {"status":"evidence_blocked","reason":name + "_governance_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if run.get("health_status") and health.get("status") and run["health_status"] != health["status"]:
        return {"status":"evidence_blocked","reason":"health_status_mismatch","execution_authority":"none","automatic_execution":False,"writes_files":False}
    return {"status":"evidence_verified","execution_authority":"none","automatic_execution":False,"automatic_repair":False,"writes_files":False,"one_next_step":True}

if __name__ == "__main__":
    print(json.dumps(verify(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
