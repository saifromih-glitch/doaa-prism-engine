REQUIRED=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow"]

def verify_terminal_state(events, execution_receipt):
    if not isinstance(events,list) or not isinstance(execution_receipt,dict):
        return {"status":"terminal_state_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"execution_completed":False}
    if any(item not in events for item in REQUIRED):
        return {"status":"terminal_state_blocked","reason":"prerequisite_missing","execution_authority":"none","automatic_execution":False,"execution_completed":False}
    if not execution_receipt.get("audited") or execution_receipt.get("execution_authority") != "none":
        return {"status":"terminal_state_blocked","reason":"receipt_not_audited_or_authority_invalid","execution_authority":"none","automatic_execution":False,"execution_completed":False}
    if execution_receipt.get("execution_completed") is not True:
        return {"status":"terminal_state_blocked","reason":"execution_not_completed","execution_authority":"none","automatic_execution":False,"execution_completed":False}
    return {"status":"terminal_state_verified","execution_authority":"none","automatic_execution":False,"execution_completed":True,"receipt_audited":True}

