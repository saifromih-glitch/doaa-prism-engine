def audit_chain(artifact, approval, gate):
    if not all(isinstance(x, dict) for x in (artifact, approval, gate)):
        return {"status":"chain_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    release = artifact.get("release_id")
    digest = artifact.get("manifest_sha256")
    if not release or not digest:
        return {"status":"chain_blocked","reason":"artifact_identity_missing","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if approval.get("reviewed_release_id") != release or approval.get("reviewed_manifest_sha256") != digest:
        return {"status":"chain_blocked","reason":"approval_binding_mismatch","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if gate.get("release_id") != release or gate.get("manifest_sha256") != digest:
        return {"status":"chain_blocked","reason":"gate_binding_mismatch","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if approval.get("execution_authority") != "none" or approval.get("execution_started") is not False:
        return {"status":"chain_blocked","reason":"approval_execution_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if gate.get("execution_authority") != "none" or gate.get("automatic_execution") is not False or gate.get("execution_started") is not False:
        return {"status":"chain_blocked","reason":"gate_execution_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"chain_verified","release_id":release,"manifest_sha256":digest,"execution_authority":"none","automatic_execution":False,"execution_started":False,"single_chain":True}

