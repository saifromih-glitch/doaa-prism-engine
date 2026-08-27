REQUIRED = {"artifact_id", "release_id", "manifest_sha256", "generated_at", "verification_status", "execution_authority", "automatic_execution", "automatic_repair", "writes_files"}
ALLOWED = {"evidence_verified", "consistency_verified"}

def approve_artifact(artifact):
    if not isinstance(artifact, dict) or set(artifact) != REQUIRED:
        return {"status":"artifact_approval_blocked","reason":"schema_incomplete","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if artifact["verification_status"] not in ALLOWED:
        return {"status":"artifact_approval_blocked","reason":"verification_status_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if any(not isinstance(artifact[k], str) or not artifact[k].strip() for k in ("artifact_id", "release_id", "manifest_sha256", "generated_at")):
        return {"status":"artifact_approval_blocked","reason":"required_value_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if artifact["execution_authority"] != "none" or artifact["automatic_execution"] is not False or artifact["automatic_repair"] is not False or artifact["writes_files"] is not False:
        return {"status":"artifact_approval_blocked","reason":"governance_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    return {"status":"artifact_approved_for_registration","execution_authority":"none","automatic_execution":False,"automatic_repair":False,"writes_files":False,"registration_authorized":False}

