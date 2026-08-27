def verify_decision_chain(approval, chain_audit):
    if not isinstance(approval, dict) or not isinstance(chain_audit, dict):
        return {"status":"decision_chain_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if chain_audit.get("status") != "chain_verified":
        return {"status":"decision_chain_blocked","reason":"chain_not_verified","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if approval.get("reviewed_release_id") != chain_audit.get("release_id") or approval.get("reviewed_manifest_sha256") != chain_audit.get("manifest_sha256"):
        return {"status":"decision_chain_blocked","reason":"decision_binding_mismatch","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if approval.get("execution_authority") != "none" or approval.get("execution_started") is not False:
        return {"status":"decision_chain_blocked","reason":"decision_execution_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"decision_chain_verified","release_id":chain_audit["release_id"],"manifest_sha256":chain_audit["manifest_sha256"],"execution_authority":"none","automatic_execution":False,"execution_started":False,"decision_bound":True}

