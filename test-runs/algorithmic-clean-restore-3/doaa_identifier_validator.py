import re
PATTERN=re.compile(r"^[A-Za-z0-9._:-]{1,96}$")

def validate_identifiers(request_id, artifact_id, release_id):
    values=(request_id,artifact_id,release_id)
    if not all(isinstance(v,str) and PATTERN.fullmatch(v) for v in values):
        return {"status":"identifier_blocked","reason":"format_invalid","execution_authority":"none","automatic_execution":False}
    return {"status":"identifier_verified","request_id":request_id,"artifact_id":artifact_id,"release_id":release_id,"execution_authority":"none","automatic_execution":False,"bounded":True}

