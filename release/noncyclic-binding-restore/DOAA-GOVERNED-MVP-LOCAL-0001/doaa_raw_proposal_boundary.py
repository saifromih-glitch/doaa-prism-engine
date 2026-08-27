ALLOWED = {"status", "message_id", "model_id", "raw_response", "execution_authority", "automatic_execution", "execution_started", "writes_files", "source_modified", "network_scope"}


def verify_raw_boundary(result):
    if not isinstance(result, dict):
        return {"status": "raw_boundary_blocked", "reason": "result_object_required", "execution_authority": "none", "automatic_execution": False}
    if result.get("status") != "ollama_raw_proposal_received":
        return {"status": "raw_boundary_blocked", "reason": "raw_result_required", "execution_authority": "none", "automatic_execution": False}
    if set(result) != ALLOWED or not isinstance(result.get("raw_response"), str):
        return {"status": "raw_boundary_blocked", "reason": "raw_schema_invalid", "execution_authority": "none", "automatic_execution": False}
    if result.get("execution_authority") != "none" or result.get("automatic_execution") is not False or result.get("execution_started") is not False or result.get("writes_files") is not False or result.get("source_modified") is not False or result.get("network_scope") != "local_ollama_only":
        return {"status": "raw_boundary_blocked", "reason": "authority_boundary_invalid", "execution_authority": "none", "automatic_execution": False}
    return {"status": "raw_boundary_verified", "raw_is_untrusted": True, "requires_gate": True, "execution_authority": "none", "automatic_execution": False}

