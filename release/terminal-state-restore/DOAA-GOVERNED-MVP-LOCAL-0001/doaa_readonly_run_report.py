import json
import sys

def build_report(payload):
    required = {"health_status", "audit_summary", "generated_at"}
    if not isinstance(payload, dict) or set(payload) != required:
        return {"status":"run_report_blocked","reason":"input_schema_invalid","execution_authority":"none","automatic_repair":False,"writes_files":False}
    if payload["health_status"] not in {"health_ok", "health_blocked"}:
        return {"status":"run_report_blocked","reason":"health_status_invalid","execution_authority":"none","automatic_repair":False,"writes_files":False}
    if not isinstance(payload["audit_summary"], dict) or not isinstance(payload["generated_at"], str) or not payload["generated_at"].strip():
        return {"status":"run_report_blocked","reason":"summary_or_timestamp_invalid","execution_authority":"none","automatic_repair":False,"writes_files":False}
    return {"status":"run_report_ready","health_status":payload["health_status"],"audit_summary":payload["audit_summary"],"generated_at":payload["generated_at"],"execution_authority":"none","automatic_repair":False,"writes_files":False,"scheduling":False,"network_request":False}

if __name__ == "__main__":
    print(json.dumps(build_report(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
