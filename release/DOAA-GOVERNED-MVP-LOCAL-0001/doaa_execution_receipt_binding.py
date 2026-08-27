def verify_receipt_binding(receipt, artifact_id, release_id, manifest_sha256, approval_id):
    expected=(artifact_id,release_id,manifest_sha256,approval_id)
    if not isinstance(receipt,dict) or not all(isinstance(v,str) and v.strip() for v in expected):
        return {"status":"receipt_binding_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False}
    actual=tuple(receipt.get(k) for k in ("artifact_id","release_id","manifest_sha256","approval_id"))
    if actual != expected:
        return {"status":"receipt_binding_blocked","reason":"receipt_context_mismatch","execution_authority":"none","automatic_execution":False}
    if receipt.get("audited") is not True or receipt.get("execution_completed") is not True:
        return {"status":"receipt_binding_blocked","reason":"receipt_not_complete_or_audited","execution_authority":"none","automatic_execution":False}
    if receipt.get("execution_authority") != "none":
        return {"status":"receipt_binding_blocked","reason":"receipt_authority_invalid","execution_authority":"none","automatic_execution":False}
    return {"status":"receipt_binding_verified","artifact_id":artifact_id,"release_id":release_id,"approval_id":approval_id,"execution_authority":"none","automatic_execution":False,"bound":True}

