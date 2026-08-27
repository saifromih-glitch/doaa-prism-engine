FORBIDDEN = {"raw_response", "secret", "password", "shell_command", "source_code", "generated_code", "write_path", "network_url"}
REQUIRED_FLAGS = {"execution_authority": "none", "automatic_execution": False, "automatic_repair": False, "writes_files": False}

def verify_boundary(artifact):
    if not isinstance(artifact, dict):
        return {"status":"boundary_blocked","reason":"artifact_not_object","execution_authority":"none","automatic_execution":False,"writes_files":False}
    forbidden = sorted(FORBIDDEN.intersection(artifact))
    if forbidden:
        return {"status":"boundary_blocked","reason":"forbidden_fields","fields":forbidden,"execution_authority":"none","automatic_execution":False,"writes_files":False}
    for key, expected in REQUIRED_FLAGS.items():
        if artifact.get(key) != expected:
            return {"status":"boundary_blocked","reason":key + "_invalid","execution_authority":"none","automatic_execution":False,"writes_files":False}
    return {"status":"boundary_verified","execution_authority":"none","automatic_execution":False,"writes_files":False,"secrets_detected":False,"write_paths_detected":False}

