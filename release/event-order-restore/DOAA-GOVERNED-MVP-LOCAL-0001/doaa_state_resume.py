import json
import sys

REQUIRED = {"status", "facts", "decisions", "checked", "changed", "unverified", "risks", "next_step"}

def validate_state(payload):
    if not isinstance(payload, dict) or set(payload) != REQUIRED:
        return {"status":"state_blocked","reason":"schema_invalid","execution_authority":"none","automatic_execution":False,"automatic_repair":False}
    if not isinstance(payload["status"], str) or not payload["status"].strip():
        return {"status":"state_blocked","reason":"status_invalid","execution_authority":"none","automatic_execution":False,"automatic_repair":False}
    for key in REQUIRED - {"status", "next_step"}:
        if not isinstance(payload[key], list):
            return {"status":"state_blocked","reason":key + "_must_be_list","execution_authority":"none","automatic_execution":False,"automatic_repair":False}
    if not isinstance(payload["next_step"], str) or not payload["next_step"].strip():
        return {"status":"state_blocked","reason":"next_step_invalid","execution_authority":"none","automatic_execution":False,"automatic_repair":False}
    return {"status":"state_ready","state":payload,"execution_authority":"none","automatic_execution":False,"automatic_repair":False,"execution_started":False}

if __name__ == "__main__":
    print(json.dumps(validate_state(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
