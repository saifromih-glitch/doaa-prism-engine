def verify_path_safety(events):
    if not isinstance(events,list) or any(not isinstance(e,str) for e in events):
        return {"status":"path_blocked","reason":"events_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    required=["proposal_received","gate_checked","human_reviewed"]
    if any(x not in events for x in required):
        return {"status":"path_blocked","reason":"prerequisite_missing","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if events.index("proposal_received") > events.index("gate_checked") or events.index("gate_checked") > events.index("human_reviewed"):
        return {"status":"path_blocked","reason":"prerequisite_order_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if "execution_started" in events:
        if "approved_for_governed_flow" not in events or events.index("execution_started") < events.index("approved_for_governed_flow"):
            return {"status":"path_blocked","reason":"execution_before_approval","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"path_verified","execution_authority":"none","automatic_execution":False,"execution_started":False,"gate_safe":True}

