ALLOWED={"proposal_received","gate_checked","human_reviewed","approved_for_governed_flow","rejected_by_human","execution_started","execution_completed"}

def validate_event_type(event_type):
    if not isinstance(event_type,str) or event_type not in ALLOWED:
        return {"status":"event_type_blocked","reason":"unknown_event_type","execution_authority":"none","automatic_execution":False}
    return {"status":"event_type_verified","event_type":event_type,"execution_authority":"none","automatic_execution":False,"known_type":True}

