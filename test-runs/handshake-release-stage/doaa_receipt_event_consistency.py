REQUIRED=["proposal_received","gate_checked","human_reviewed","approved_for_governed_flow","execution_started","execution_completed"]
IDENTITY=["request_id","artifact_id","release_id","manifest_sha256"]

def verify_receipt_events(receipt, events):
    if not isinstance(receipt,dict) or not isinstance(events,list) or any(not isinstance(e,dict) for e in events):
        return {"status":"receipt_events_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False}
    types=[e.get("event_type") for e in events]
    if types != REQUIRED:
        return {"status":"receipt_events_blocked","reason":"event_order_invalid","execution_authority":"none","automatic_execution":False}
    for key in IDENTITY:
        if not isinstance(receipt.get(key),str) or not receipt[key].strip() or any(e.get(key) != receipt[key] for e in events):
            return {"status":"receipt_events_blocked","reason":"identity_mismatch","execution_authority":"none","automatic_execution":False}
    if receipt.get("audited") is not True or receipt.get("execution_completed") is not True or receipt.get("execution_authority") != "none":
        return {"status":"receipt_events_blocked","reason":"receipt_state_invalid","execution_authority":"none","automatic_execution":False}
    return {"status":"receipt_events_verified","execution_authority":"none","automatic_execution":False,"execution_completed":True,"identity_bound":True,"ordered":True}

