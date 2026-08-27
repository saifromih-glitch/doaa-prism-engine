import re
FORBIDDEN = re.compile(r"(?i)\b(shell|powershell|cmd|exec|eval|subprocess|write_path|delete|publish|deploy)\b")

def validate_next_step(next_step):
    if not isinstance(next_step, str) or not next_step.strip():
        return {"status":"next_step_blocked","reason":"empty_or_non_string","execution_authority":"none","automatic_execution":False,"execution_started":False}
    if "\n" in next_step or "\r" in next_step or FORBIDDEN.search(next_step):
        return {"status":"next_step_blocked","reason":"unsafe_or_multiple_step","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"next_step_verified","next_step":next_step.strip(),"execution_authority":"none","automatic_execution":False,"execution_started":False,"descriptive_only":True}

