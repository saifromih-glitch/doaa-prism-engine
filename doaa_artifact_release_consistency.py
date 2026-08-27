import hashlib
import json

def verify_consistency(artifact, manifest_release_id, manifest_sha256):
    if not isinstance(artifact, dict) or not isinstance(manifest_release_id, str) or not isinstance(manifest_sha256, str):
        return {"status":"consistency_blocked","reason":"input_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if not artifact.get("artifact_id") or artifact.get("release_id") != manifest_release_id:
        return {"status":"consistency_blocked","reason":"release_id_mismatch","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if artifact.get("manifest_sha256") != manifest_sha256:
        return {"status":"consistency_blocked","reason":"manifest_hash_mismatch","execution_authority":"none","automatic_execution":False,"writes_files":False}
    if artifact.get("execution_authority") != "none" or artifact.get("automatic_execution") is not False:
        return {"status":"consistency_blocked","reason":"governance_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    return {"status":"consistency_verified","execution_authority":"none","automatic_execution":False,"writes_files":False,"release_bound":True}

