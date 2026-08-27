def verify_event_context(event, request_id, artifact_id, release_id):
    if not isinstance(event,dict) or set(event) != {"event_type","request_id","artifact_id","release_id"}:
        return {"status":"event_context_blocked","reason":"event_shape_invalid","execution_authority":"none","automatic_execution":False}
    expected=(request_id,artifact_id,release_id)
    actual=(event["request_id"],event["artifact_id"],event["release_id"])
    if not all(isinstance(v,str) and v.strip() for v in expected) or actual != expected:
        return {"status":"event_context_blocked","reason":"context_mismatch","execution_authority":"none","automatic_execution":False}
    return {"status":"event_context_verified","execution_authority":"none","automatic_execution":False,"exact_match":True}

