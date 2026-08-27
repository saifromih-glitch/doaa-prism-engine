ALLOWED={"approved_for_governed_flow","rejected_by_human"}

def verify_separation(approval_result):
    if not isinstance(approval_result, dict):
        return {"status":"separation_blocked","reason":"not_object","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if approval_result.get("status") not in ALLOWED:
        return {"status":"separation_blocked","reason":"status_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if approval_result.get("execution_authority") != "none" or approval_result.get("automatic_execution") is not False or approval_result.get("execution_started") is not False:
        return {"status":"separation_blocked","reason":"execution_not_separate","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"separation_verified","approval_status":approval_result["status"],"execution_authority":"none","automatic_execution":False,"execution_started":False,"gate_only":True}

