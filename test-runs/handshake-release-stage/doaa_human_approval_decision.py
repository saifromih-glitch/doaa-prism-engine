ALLOWED = {"approve_for_governed_flow", "reject"}

def record_decision(artifact_id, reviewer_decision, reviewed_release_id, reviewed_manifest_sha256):
    if not all(isinstance(v, str) and v.strip() for v in (artifact_id, reviewer_decision, reviewed_release_id, reviewed_manifest_sha256)):
        return {"status":"approval_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if reviewer_decision not in ALLOWED:
        reviewer_decision = "reject"
    if reviewer_decision == "approve_for_governed_flow":
        return {"status":"approved_for_governed_flow","artifact_id":artifact_id,"reviewed_release_id":reviewed_release_id,"reviewed_manifest_sha256":reviewed_manifest_sha256,"execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"rejected_by_human","artifact_id":artifact_id,"reviewed_release_id":reviewed_release_id,"reviewed_manifest_sha256":reviewed_manifest_sha256,"execution_authority":"none","automatic_execution":False,"execution_started":False}

