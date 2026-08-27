import json
from pathlib import Path

ALLOWED = {"status", "execution_authority", "automatic_execution", "automatic_repair", "writes_files", "one_next_step"}

def build_artifact(verification_result, artifact_id, generated_at):
    if not isinstance(verification_result, dict) or not isinstance(artifact_id, str) or not artifact_id.strip() or not isinstance(generated_at, str) or not generated_at.strip():
        return {"status":"artifact_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if set(verification_result) - ALLOWED:
        return {"status":"artifact_blocked","reason":"unapproved_fields","execution_authority":"none","automatic_execution":False,"writes_files":False}
    artifact = {"artifact_id":artifact_id,"generated_at":generated_at,"verification":{k:verification_result[k] for k in sorted(verification_result)},"execution_authority":"none","automatic_execution":False,"writes_files":False}
    return {"status":"artifact_ready","artifact":artifact,"execution_authority":"none","automatic_execution":False,"writes_files":False}

def write_artifact(path, result):
    if not isinstance(result, dict) or result.get("status") != "artifact_ready":
        return {"status":"artifact_blocked","reason":"not_ready","execution_authority":"none","automatic_execution":False,"writes_files":False}
    Path(path).write_text(json.dumps(result["artifact"], ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {"status":"artifact_written","path":str(path),"execution_authority":"none","automatic_execution":False,"writes_files":True}

