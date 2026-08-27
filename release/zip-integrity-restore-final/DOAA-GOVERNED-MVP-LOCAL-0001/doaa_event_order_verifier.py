ALLOWED={"proposal_received","gate_checked","human_reviewed","approved_for_governed_flow","rejected_by_human","execution_started","execution_completed"}
REQUIRED=["proposal_received","gate_checked","human_reviewed"]

def verify_event_order(events):
    if not isinstance(events,list) or not events or any(not isinstance(e,str) or e not in ALLOWED for e in events):
        return {"status":"event_order_blocked","reason":"events_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if len(events) != len(set(events)):
        return {"status":"event_order_blocked","reason":"duplicate_event","execution_authority":"none","automatic_execution":False,"execution_started":False}
    positions=[]
    for name in REQUIRED:
        if name not in events:
            return {"status":"event_order_blocked","reason":"required_event_missing","execution_authority":"none","automatic_execution":False,"execution_started":False}
        positions.append(events.index(name))
    if positions != sorted(positions):
        return {"status":"event_order_blocked","reason":"required_order_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if "execution_started" in events and events.index("execution_started") < events.index("human_reviewed"):
        return {"status":"event_order_blocked","reason":"execution_before_review","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"event_order_verified","event_count":len(events),"execution_authority":"none","automatic_execution":False,"execution_started":False,"ordered":True}

