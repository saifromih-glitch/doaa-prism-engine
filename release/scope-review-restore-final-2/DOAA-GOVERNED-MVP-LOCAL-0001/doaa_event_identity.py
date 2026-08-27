def verify_event_identity(events, request_id, artifact_id, release_id):
    ids=(request_id, artifact_id, release_id)
    if not isinstance(events,list) or not all(isinstance(x,str) and x.strip() for x in ids):
        return {"status":"event_identity_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False}
    for event in events:
        if not isinstance(event,dict) or set(event) != {"event_type","request_id","artifact_id","release_id"}:
            return {"status":"event_identity_blocked","reason":"event_shape_invalid","execution_authority":"none","automatic_execution":False}
        if (event["request_id"],event["artifact_id"],event["release_id"]) != ids:
            return {"status":"event_identity_blocked","reason":"mixed_identity","execution_authority":"none","automatic_execution":False}
    return {"status":"event_identity_verified","event_count":len(events),"execution_authority":"none","automatic_execution":False,"single_identity":True}

