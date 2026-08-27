REQUIRED={"proposal","gate","human_review","approval","execution_receipt","manifest_binding"}
FORBIDDEN={"raw_response","password","secret","token","source_code","write_path"}

def verify_final_audit(evidence):
    if not isinstance(evidence,dict) or set(evidence) != REQUIRED:
        return {"status":"final_audit_blocked","reason":"evidence_incomplete","execution_authority":"none","automatic_execution":False}
    if any(not isinstance(v,dict) for v in evidence.values()):
        return {"status":"final_audit_blocked","reason":"evidence_shape_invalid","execution_authority":"none","automatic_execution":False}
    if any(key in evidence or any(key in item for item in evidence.values()) for key in FORBIDDEN):
        return {"status":"final_audit_blocked","reason":"sensitive_or_internal_field","execution_authority":"none","automatic_execution":False}
    if not all(item.get("verified") is True for item in evidence.values()):
        return {"status":"final_audit_blocked","reason":"evidence_not_verified","execution_authority":"none","automatic_execution":False}
    return {"status":"final_audit_verified","evidence_count":len(evidence),"execution_authority":"none","automatic_execution":False,"complete":True}

