REQUIRED=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]
ALLOWED={"not_started","ready_for_separate_safe_executor"}

def verify_execution_state(events, execution_state):
    if not isinstance(events,list) or execution_state not in ALLOWED:
        return {"status":"execution_state_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if any(item not in events for item in REQUIRED):
        return {"status":"execution_state_blocked","reason":"prerequisite_missing","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if execution_state == "ready_for_separate_safe_executor" and "execution_started" in events:
        return {"status":"execution_state_blocked","reason":"execution_already_started","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if events.index("approved_for_governed_flow") < events.index("human_reviewed"):
        return {"status":"execution_state_blocked","reason":"approval_order_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"execution_state_verified","execution_state":execution_state,"execution_authority":"none","automatic_execution":False,"execution_started":False,"consistent":True}

