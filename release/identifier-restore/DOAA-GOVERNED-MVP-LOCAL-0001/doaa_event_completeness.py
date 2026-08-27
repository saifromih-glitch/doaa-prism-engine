REQUIRED={"proposal_received","gate_checked","human_reviewed"}
ALLOWED={"approved_for_governed_flow","rejected_by_human"}

def verify_completeness(events, artifact_id, release_id, manifest_sha256, approval_status):
    if not isinstance(events,list) or not isinstance(artifact_id,str) or not isinstance(release_id,str) or not isinstance(manifest_sha256,str) or approval_status not in ALLOWED:
        return {"status":"event_completeness_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if not artifact_id.strip() or not release_id.strip() or not manifest_sha256.strip() or any(e not in REQUIRED for e in events):
        return {"status":"event_completeness_blocked","reason":"identity_or_event_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if set(events) != REQUIRED or len(events) != len(REQUIRED):
        return {"status":"event_completeness_blocked","reason":"required_events_incomplete","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if events != ["proposal_received","gate_checked","human_reviewed"]:
        return {"status":"event_completeness_blocked","reason":"event_order_invalid","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"event_completeness_verified","artifact_id":artifact_id,"release_id":release_id,"manifest_sha256":manifest_sha256,"approval_status":approval_status,"execution_authority":"none","automatic_execution":False,"execution_started":False,"complete":True}

