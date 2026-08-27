def verify_idempotent_transition(events, transition):
    if not isinstance(events,list) or not isinstance(transition,(list,tuple)) or len(transition) != 2:
        return {"status":"idempotency_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False}
    if len(events) != len(set(events)):
        return {"status":"idempotency_blocked","reason":"duplicate_event","execution_authority":"none","automatic_execution":False}
    if events.count("approved_for_governed_flow") > 1:
        return {"status":"idempotency_blocked","reason":"reapproval_detected","execution_authority":"none","automatic_execution":False}
    if events.count("execution_started") > 1 or events.count("execution_completed") > 1:
        return {"status":"idempotency_blocked","reason":"reexecution_detected","execution_authority":"none","automatic_execution":False}
    if list(transition) == ["approved_for_governed_flow","execution_started"]:
        return {"status":"idempotency_blocked","reason":"execution_transition_requires_separate_executor","execution_authority":"none","automatic_execution":False}
    return {"status":"idempotency_verified","transition":list(transition),"execution_authority":"none","automatic_execution":False,"single_application":True}

